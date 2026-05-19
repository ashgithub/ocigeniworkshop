""" What this file does:
Demonstrates the OCI vector store connector REST workflow:
1) Build OCI user auth with `OpenAIClientProvider.get_raw_user_auth()`.
2) Resolve the vector store, Object Storage bucket, and connector endpoint.
3) Create a connector that ingests files from Object Storage.
4) List and retrieve connector details.
5) Update connector metadata.
6) Inspect connector stats and ingestion logs.
7) Optionally trigger, inspect, cancel, and log a manual file sync.
8) Optionally delete the connector.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Configure OCI credentials, project, compartment, and profile in `sandbox.yaml`.
- Set `oci.unstructured_vector_store_id` in `sandbox.yaml`.
- Set `bucket.namespace` and `bucket.bucketName` in `sandbox.yaml`.
- Optionally set `bucket.prefix` or `VECTOR_OS_PREFIXES` to limit ingestion.

How to run the file:
uv run openai_sdk/genai_client/vector_store/vector_store_connector.py

Safe experiments:
1. Use a small Object Storage prefix while learning.
2. Keep `DELETE_CONNECTOR_AT_END=False` until you confirm connector behavior.
3. Keep `CANCEL_FILE_SYNC_IMMEDIATELY=False` unless you want to test cancel behavior.

Important sections:
1. Step 1: Load provider and derive the connector endpoint.
2. Step 2: Resolve vector store and Object Storage source values.
3. Step 3: Create the connector.
4. Step 4-8: Inspect connector list, details, stats, and logs.
5. Step 9-12: Optional manual file sync flow.
6. Step 13: Optional connector cleanup.
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
    """Return the OCI connector control-plane endpoint in `/20231130` form."""
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
    """Send one REST request and return JSON so the main flow stays readable."""
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
    """Build the Object Storage connector payload expected by the OCI endpoint."""
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
    """Read a sync-count bucket from the stats response, defaulting to zero."""
    return (stats.get(key) or {}).get("totalFilesSynced", 0)


def main() -> None:
    # Step 1: Load repo-standard provider config and derive the connector
    # control-plane endpoint used by the REST calls below.
    print("Step 1 - Loading provider and deriving connector endpoint.")
    provider = OpenAIClientProvider()
    endpoint = connector_endpoint(provider)
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "OpenAI-Project": provider.oci_openai_project,
        "opc-compartment-id": provider.oci_compartment_id,
        "compartment-id": provider.oci_compartment_id,
    }

    # Step 2: Resolve vector store and Object Storage source values. Beginners
    # usually only need to edit sandbox.yaml for this step.
    print("Step 2 - Resolving vector store and Object Storage source values.")
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
        # Step 3: Create a connector that knows which bucket and prefixes should
        # feed files into the vector store.
        print("Step 3 - Creating vector store connector.")
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

        # Step 4: List connectors for this vector store so learners can compare
        # the new connector with any existing connectors.
        print("Step 4 - Listing connectors for this vector store.")
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

        # Step 5: Retrieve the connector directly by id for full details.
        print("Step 5 - Fetching connector details.")
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

        # Step 6: Optionally update connector metadata. This does not change the
        # bucket source; it only demonstrates the update endpoint.
        print("Step 6 - Checking whether connector metadata update is enabled.")
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

        # Step 7: Read sync statistics to understand how many files were created,
        # updated, ignored, failed, or are still in progress.
        print("Step 7 - Reading connector sync statistics.")
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

        # Step 8: Read connector-wide ingestion logs. These are useful when a
        # connector runs on schedule and you want to inspect recent events.
        print("Step 8 - Reading connector-wide ingestion logs.")
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
        # Step 9: Optionally trigger a manual sync run for this connector.
        print("Step 9 - Checking whether manual file sync is enabled.")
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
            # Step 10: List and retrieve file sync runs so you can inspect
            # lifecycle state and timing for the manual sync.
            print("Step 10 - Inspecting file sync run.")
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

            # Step 11: Optionally cancel the file sync. The default keeps the
            # sync running so beginners can observe normal ingestion.
            print("Step 11 - Checking whether file sync cancel is enabled.")
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

            # Step 12: Read ingestion logs scoped to the manual sync run.
            print("Step 12 - Reading sync-level ingestion logs.")
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

        # Step 13: Optional cleanup. The default is to keep the connector so you
        # can inspect it in OCI Console after the script finishes.
        print("Step 13 - Checking whether connector cleanup is enabled.")
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
