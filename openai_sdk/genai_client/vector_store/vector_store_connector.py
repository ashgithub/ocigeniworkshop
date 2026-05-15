"""Run vector store connector APIs with the repo-standard OCI user auth.

This file is intentionally a direct REST probe:
1) Build auth from OpenAIClientProvider.get_raw_user_auth()
2) Create a vector store connector
3) Inspect connector details, stats, logs, and optional file sync

Run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_store_connector.py
"""

import os
import sys

import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider


VECTOR_OS_PREFIXES = []  # Leave empty to ingest the entire bucket, or set values like ["docs/"].
CONNECTOR_ENDPOINT = ""  # Leave empty to derive from provider.oci_openai_vector_endpoint.
CONNECTOR_DISPLAY_NAME = "workshop-vector-connector"
CONNECTOR_DESCRIPTION = "Connector sample created by vector_store_connector.py"
UPDATE_CONNECTOR_AFTER_CREATE = True
UPDATED_CONNECTOR_DESCRIPTION = "Connector sample updated by vector_store_connector.py"
TRIGGER_FILE_SYNC = True
FILE_SYNC_DISPLAY_NAME = "workshop-vector-connector-sync"
CANCEL_FILE_SYNC_IMMEDIATELY = False
DELETE_CONNECTOR_AT_END = False
REQUEST_TIMEOUT_SECONDS = 120.0

def connector_endpoint(provider: OpenAIClientProvider) -> str:
    endpoint = (
        CONNECTOR_ENDPOINT
        or getattr(provider, "oci_openai_connector_endpoint", "")
        or getattr(provider, "oci_openai_vector_endpoint", "")
        or provider.get_sandbox_value("oci", "connector_endpoint", "")
        or provider.get_sandbox_value("oci", "vector_endpoint", "")
        or "https://generativeai.us-chicago-1.oci.oraclecloud.com/20231130"
    ).rstrip("/")
    if "/openai/v1" in endpoint:
        endpoint = endpoint.split("/openai/v1", 1)[0]
    if not endpoint.endswith("/20231130"):
        endpoint = f"{endpoint}/20231130"
    return endpoint


def request_json(
    client: httpx.Client,
    method: str,
    endpoint: str,
    path: str,
    headers: dict[str, str],
    params: dict | None = None,
    body: dict | None = None,
) -> dict:
    response = client.request(
        method,
        f"{endpoint}{path}",
        headers=headers,
        params=params,
        json=body,
    )
    response.raise_for_status()
    return response.json() if response.content else {}


def connector_body(
    compartment_id: str,
    vector_store_id: str,
    namespace: str,
    bucket_name: str,
    storage_prefixes: list[str],
) -> dict:
    return {
        "compartmentId": compartment_id,
        "vectorStoreId": vector_store_id,
        "displayName": CONNECTOR_DISPLAY_NAME,
        "description": CONNECTOR_DESCRIPTION,
        "configuration": {
            "type": "OBJECT_STORAGE_FILES",
            "storageConfigList": [
                {
                    "namespace": namespace,
                    "bucketName": bucket_name,
                    "prefixList": storage_prefixes,
                }
            ],
        },
        "scheduleConfig": {
            "configType": "INTERVAL",
            "frequency": "DAILY",
            "interval": 1,
            "state": "ENABLED",
        },
    }


def total_synced(stats: dict, key: str) -> int:
    return (stats.get(key) or {}).get("totalFilesSynced", 0)


def main() -> None:
    provider = OpenAIClientProvider()
    endpoint = connector_endpoint(provider)
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "OpenAI-Project": provider.oci_openai_project,
        "opc-compartment-id": provider.oci_compartment_id,
        "compartment-id": provider.oci_compartment_id,
    }

    compartment_id = provider.oci_compartment_id
    vector_store_id = (
        getattr(provider, "oci_openai_unstructured_vector_store_id", "")
        or provider.get_sandbox_value("oci", "unstructured_vector_store_id", "")
        or provider.get_sandbox_value("oci", "vector_store_id", "")
        or os.getenv("VECTOR_STORE_ID", "").strip()
    )
    if not vector_store_id:
        raise ValueError("Missing unstructured vector store id in sandbox.yaml.")

    namespace = provider.get_sandbox_value("bucket", "namespace", "") or ""
    bucket_name = provider.get_sandbox_value("bucket", "bucketName", "") or ""
    sandbox_prefix = provider.get_sandbox_value("bucket", "prefix", "") or ""

    namespace = namespace or os.getenv("VECTOR_OS_NAMESPACE", "").strip()
    bucket_name = bucket_name or os.getenv("VECTOR_OS_BUCKET", "").strip()
    sandbox_prefix = sandbox_prefix or os.getenv("VECTOR_OS_PREFIX", "").strip()

    if not namespace or not bucket_name:
        raise ValueError(
            "Missing object storage namespace/bucket. Use sandbox.yaml -> bucket.namespace "
            "and bucket.bucketName, or set VECTOR_OS_NAMESPACE and VECTOR_OS_BUCKET."
        )

    storage_prefixes = VECTOR_OS_PREFIXES or ([sandbox_prefix] if sandbox_prefix else [])
    print(f"Using endpoint: {endpoint}")
    print(f"Using OCI profile: {provider.oci_openai_profile}")
    print(f"Using vector store id: {vector_store_id}")
    print(f"Using object storage source: oci://{namespace}/{bucket_name}")
    print(f"Using prefixes: {storage_prefixes if storage_prefixes else '[entire bucket]'}")

    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, auth=provider.get_raw_user_auth()) as client:
        connector = request_json(
            client,
            "POST",
            endpoint,
            "/vectorStoreConnectors",
            headers,
            body=connector_body(
                compartment_id,
                vector_store_id,
                namespace,
                bucket_name,
                storage_prefixes,
            ),
        )
        connector_id = connector["id"]
        print(f"Connector created: {connector_id} ({connector.get('lifecycleState')})")

        connectors = request_json(
            client,
            "GET",
            endpoint,
            "/vectorStoreConnectors",
            headers,
            params={"compartmentId": compartment_id, "vectorStoreId": vector_store_id},
        ).get("items", [])
        print(f"Total connectors: {len(connectors)}")
        for item in connectors[:10]:
            print(
                f"Connector list item: {item.get('id')} | "
                f"{item.get('lifecycleState')} | {item.get('displayName')}"
            )

        fetched = request_json(
            client,
            "GET",
            endpoint,
            f"/vectorStoreConnectors/{connector_id}",
            headers,
        )
        print("Fetched connector details:")
        print(f"id: {fetched.get('id')}")
        print(f"display_name: {fetched.get('displayName')}")
        print(f"description: {fetched.get('description')}")
        print(f"lifecycle_state: {fetched.get('lifecycleState')}")
        print(f"vector_store_id: {fetched.get('vectorStoreId')}")
        print(f"time_created: {fetched.get('timeCreated')}")

        if UPDATE_CONNECTOR_AFTER_CREATE:
            updated_connector = request_json(
                client,
                "PUT",
                endpoint,
                f"/vectorStoreConnectors/{connector_id}",
                headers,
                body={
                    "displayName": CONNECTOR_DISPLAY_NAME,
                    "description": UPDATED_CONNECTOR_DESCRIPTION,
                },
            )
            print("Updated connector metadata:")
            print(f"display_name: {updated_connector.get('displayName')}")
            print(f"description: {updated_connector.get('description')}")
            print(f"lifecycle_state: {updated_connector.get('lifecycleState')}")
        else:
            print("Skipping connector update.")

        stats = request_json(
            client,
            "GET",
            endpoint,
            f"/vectorStoreConnectors/{connector_id}/stats",
            headers,
        )
        print("Connector sync statistics:")
        print(f"time_generated: {stats.get('timeGenerated')}")
        print(f"created: {total_synced(stats, 'created')}")
        print(f"updated: {total_synced(stats, 'updated')}")
        print(f"deleted: {total_synced(stats, 'deleted')}")
        print(f"failed: {total_synced(stats, 'failed')}")
        print(f"in_progress: {total_synced(stats, 'inProgress')}")
        print(f"ignored: {total_synced(stats, 'ignored')}")
        print(f"unsupported: {total_synced(stats, 'unsupported')}")
        print(f"metadata_updated: {total_synced(stats, 'metadataUpdated')}")

        connector_logs = request_json(
            client,
            "GET",
            endpoint,
            f"/vectorStoreConnectors/{connector_id}/ingestionLogs",
            headers,
            params={"limit": 10},
        ).get("items", [])
        print(f"Returned connector-wide ingestion log entries: {len(connector_logs)}")
        for entry in connector_logs:
            print(entry)

        file_sync_id = None
        if TRIGGER_FILE_SYNC:
            file_sync = request_json(
                client,
                "POST",
                endpoint,
                "/vectorStoreConnectorFileSyncs",
                headers,
                body={
                    "vectorStoreConnectorId": connector_id,
                    "displayName": FILE_SYNC_DISPLAY_NAME,
                },
            )
            file_sync_id = file_sync["id"]
            print("Created file sync run:")
            print(f"id: {file_sync.get('id')}")
            print(f"display_name: {file_sync.get('displayName')}")
            print(f"lifecycle_state: {file_sync.get('lifecycleState')}")
            print(f"trigger_type: {file_sync.get('triggerType')}")
        else:
            print("Skipping manual file sync.")

        if file_sync_id:
            sync_runs = request_json(
                client,
                "GET",
                endpoint,
                "/vectorStoreConnectorFileSyncs",
                headers,
                params={
                    "compartmentId": compartment_id,
                    "vectorStoreConnectorId": connector_id,
                },
            ).get("items", [])
            print(f"Total file sync runs for connector: {len(sync_runs)}")
            for item in sync_runs[:10]:
                print(
                    f"File sync list item: {item.get('id')} | "
                    f"{item.get('lifecycleState')} | {item.get('displayName')}"
                )

            fetched_sync = request_json(
                client,
                "GET",
                endpoint,
                f"/vectorStoreConnectorFileSyncs/{file_sync_id}",
                headers,
            )
            print("Fetched file sync details:")
            print(f"id: {fetched_sync.get('id')}")
            print(f"display_name: {fetched_sync.get('displayName')}")
            print(f"lifecycle_state: {fetched_sync.get('lifecycleState')}")
            print(f"lifecycle_details: {fetched_sync.get('lifecycleDetails')}")
            print(f"trigger_type: {fetched_sync.get('triggerType')}")
            print(f"time_started: {fetched_sync.get('timeStarted')}")
            print(f"time_ended: {fetched_sync.get('timeEnded')}")
            print(f"duration_in_seconds: {fetched_sync.get('durationInSeconds')}")

            if CANCEL_FILE_SYNC_IMMEDIATELY:
                request_json(
                    client,
                    "DELETE",
                    endpoint,
                    f"/vectorStoreConnectorFileSyncs/{file_sync_id}",
                    headers,
                )
                print(f"Cancel request accepted for file sync: {file_sync_id}")
                fetched_sync = request_json(
                    client,
                    "GET",
                    endpoint,
                    f"/vectorStoreConnectorFileSyncs/{file_sync_id}",
                    headers,
                )
                print(f"Post-cancel lifecycle_state: {fetched_sync.get('lifecycleState')}")
            else:
                print("Skipping file sync cancel.")

            sync_logs = request_json(
                client,
                "GET",
                endpoint,
                f"/vectorStoreConnectorFileSyncs/{file_sync_id}/ingestionLogs",
                headers,
                params={"limit": 10},
            ).get("items", [])
            print(f"Returned sync-level ingestion log entries: {len(sync_logs)}")
            for entry in sync_logs:
                print(entry)

        if DELETE_CONNECTOR_AT_END:
            request_json(
                client,
                "DELETE",
                endpoint,
                f"/vectorStoreConnectors/{connector_id}",
                headers,
            )
            print(f"Delete request sent for {connector_id}")
        else:
            print("Skipping delete. Set DELETE_CONNECTOR_AT_END=True to delete connector.")


if __name__ == "__main__":
    main()
