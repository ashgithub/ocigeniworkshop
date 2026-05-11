"""What this file does:
Runs vector store connector APIs in one walkthrough:
1) Create connector
2) List connectors
3) Get connector details
4) Optionally update connector metadata
5) Get connector stats
6) List connector-wide ingestion logs
7) Trigger a manual file sync
8) List file sync runs
9) Get one file sync run
10) Optionally cancel a file sync run
11) List sync-level ingestion logs
12) Optionally delete connector

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- OCI Generative AI control-plane docs (connector-related): internal GA guide
  https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Set a valid `oci.vector_store_id` in `sandbox.yaml`.
- Ensure `bucket.namespace` and `bucket.bucketName` exist in `sandbox.yaml`.
- Make sure the bucket already contains files under the selected prefix.
- Required IAM policy from the GA guide:
  allow any-user to read object-family in compartment <COMPARTMENT_NAME>
  where ALL {request.principal.type='generativeaivectorconnector'}

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_store_connector.py

Safe experiments:
1. Run with `DELETE_CONNECTOR_AT_END=False` to inspect created connector state.
2. Keep `TRIGGER_FILE_SYNC=True` to test ingestion immediately after creation.
3. Adjust `VECTOR_OS_PREFIXES` to scope ingestion to a folder-like prefix in the bucket.

Important sections:
1. Step 1: Build OCI control-plane client.
2. Step 2: Resolve runtime values.
3. Step 3-7: Execute connector lifecycle operations.
4. Step 8-12: Execute file sync lifecycle operations.
"""

import os
import sys
import oci

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

VECTOR_OS_PREFIXES = []  # Leave empty to ingest the entire bucket, or set values like ["docs/"].
CONNECTOR_DISPLAY_NAME = "workshop-vector-connector"
CONNECTOR_DESCRIPTION = "Connector sample created by vector_store_connector.py"
UPDATE_CONNECTOR_AFTER_CREATE = True
UPDATED_CONNECTOR_DESCRIPTION = "Connector sample updated by vector_store_connector.py"
TRIGGER_FILE_SYNC = True
FILE_SYNC_DISPLAY_NAME = "workshop-vector-connector-sync"
CANCEL_FILE_SYNC_IMMEDIATELY = False
DELETE_CONNECTOR_AT_END = False

def main():
    # Step 1: Build the OCI control-plane client from OpenAIClientProvider.
    provider = OpenAIClientProvider()
    client, compartment_id = provider.build_oci_generative_ai_control_plane_client()

    # Step 2: Resolve required values.
    vector_store_id = provider.oci_openai_vector_store_id
    if not vector_store_id:
        raise ValueError(
            "Missing vector store id. Set `oci.vector_store_id` in sandbox.yaml."
        )

    # Prefer sandbox.yaml bucket values for beginner setup so the script works with repo defaults.
    namespace = provider.get_sandbox_value("bucket", "namespace", "") or ""
    bucket_name = provider.get_sandbox_value("bucket", "bucketName", "") or ""
    sandbox_prefix = provider.get_sandbox_value("bucket", "prefix", "") or ""

    # If missing in sandbox config, allow env overrides.
    namespace = namespace or os.getenv("VECTOR_OS_NAMESPACE", "").strip()
    bucket_name = bucket_name or os.getenv("VECTOR_OS_BUCKET", "").strip()
    sandbox_prefix = sandbox_prefix or os.getenv("VECTOR_OS_PREFIX", "").strip()
    if not namespace or not bucket_name:
        raise ValueError(
            "Missing object storage namespace/bucket. "
            "Use sandbox.yaml -> bucket.namespace and bucket.bucketName, "
            "or create env vars VECTOR_OS_NAMESPACE and VECTOR_OS_BUCKET."
        )

    storage_prefixes = VECTOR_OS_PREFIXES or ([sandbox_prefix] if sandbox_prefix else [])
    print(f"Using vector store id: {vector_store_id}")
    print(f"Using object storage source: oci://{namespace}/{bucket_name}")
    print(f"Using prefixes: {storage_prefixes if storage_prefixes else '[entire bucket]'}")

    # Step 3: Create connector.
    details = oci.generative_ai.models.CreateVectorStoreConnectorDetails(
        compartment_id=compartment_id,
        vector_store_id=vector_store_id,
        display_name=CONNECTOR_DISPLAY_NAME,
        description=CONNECTOR_DESCRIPTION,
        configuration=oci.generative_ai.models.OciObjectStorageConfiguration(
            storage_config_list=[
                oci.generative_ai.models.ObjectStorageConfig(
                    namespace=namespace,
                    bucket_name=bucket_name,
                    prefix_list=storage_prefixes,
                )
            ]
        ),
        schedule_config=oci.generative_ai.models.ScheduleIntervalConfig(
            config_type="INTERVAL",
            frequency="DAILY",
            interval=1,
            state="ENABLED",
        ),
    )
    create_response = client.create_vector_store_connector(details)
    connector = create_response.data
    connector_id = connector.id
    print(f"Connector created: {connector_id} ({connector.lifecycle_state})")

    # Step 4: List connectors.
    connectors = client.list_vector_store_connectors(compartment_id=compartment_id).data.items
    print(f"Total connectors: {len(connectors)}")
    for item in connectors[:10]:
        print(f"Connector list item: {item.id} | {item.lifecycle_state} | {item.display_name}")

    # Step 5: Get connector.
    fetched = client.get_vector_store_connector(connector_id).data
    print("Fetched connector details:")
    print(f"id: {fetched.id}")
    print(f"display_name: {fetched.display_name}")
    print(f"description: {fetched.description}")
    print(f"lifecycle_state: {fetched.lifecycle_state}")
    print(f"vector_store_id: {fetched.vector_store_id}")
    print(f"time_created: {fetched.time_created}")

    # Step 6: Optionally update connector metadata.
    if UPDATE_CONNECTOR_AFTER_CREATE:
        update_details = oci.generative_ai.models.UpdateVectorStoreConnectorDetails(
            display_name=CONNECTOR_DISPLAY_NAME,
            description=UPDATED_CONNECTOR_DESCRIPTION,
        )
        updated_connector = client.update_vector_store_connector(
            connector_id,
            update_details,
        ).data
        print("Updated connector metadata:")
        print(f"display_name: {updated_connector.display_name}")
        print(f"description: {updated_connector.description}")
        print(f"lifecycle_state: {updated_connector.lifecycle_state}")
    else:
        print(
            "Skipping connector update. "
            "Set UPDATE_CONNECTOR_AFTER_CREATE=True to demonstrate the update endpoint."
        )

    # Step 7: Get connector stats and connector-wide ingestion logs.
    stats = client.get_vector_store_connector_stats(connector_id).data
    print("Connector sync statistics:")
    print(f"time_generated: {stats.time_generated}")
    print(f"created: {stats.created.total_files_synced if stats.created else 0}")
    print(f"updated: {stats.updated.total_files_synced if stats.updated else 0}")
    print(f"deleted: {stats.deleted.total_files_synced if stats.deleted else 0}")
    print(f"failed: {stats.failed.total_files_synced if stats.failed else 0}")
    print(f"in_progress: {stats.in_progress.total_files_synced if stats.in_progress else 0}")
    print(f"ignored: {stats.ignored.total_files_synced if stats.ignored else 0}")
    print(f"unsupported: {stats.unsupported.total_files_synced if stats.unsupported else 0}")
    print(
        f"metadata_updated: "
        f"{stats.metadata_updated.total_files_synced if stats.metadata_updated else 0}"
    )

    connector_logs = client.list_vector_store_connector_ingestion_logs(
        connector_id,
        limit=10,
    ).data.items
    print(f"Returned connector-wide ingestion log entries: {len(connector_logs)}")
    for entry in connector_logs:
        print(entry)

    # Step 8: Trigger a manual file sync to test ingestion immediately.
    file_sync_id = None
    if TRIGGER_FILE_SYNC:
        sync_details = oci.generative_ai.models.CreateVectorStoreConnectorFileSyncDetails(
            vector_store_connector_id=connector_id,
            display_name=FILE_SYNC_DISPLAY_NAME,
        )
        file_sync = client.create_vector_store_connector_file_sync(sync_details).data
        file_sync_id = file_sync.id
        print("Created file sync run:")
        print(f"id: {file_sync.id}")
        print(f"display_name: {file_sync.display_name}")
        print(f"lifecycle_state: {file_sync.lifecycle_state}")
        print(f"trigger_type: {file_sync.trigger_type}")
    else:
        print(
            "Skipping manual file sync. "
            "Set TRIGGER_FILE_SYNC=True to demonstrate immediate ingestion."
        )

    # Step 9-11: Inspect file sync lifecycle if a sync was created.
    if file_sync_id:
        sync_runs = client.list_vector_store_connector_file_syncs(
            compartment_id,
            vector_store_connector_id=connector_id,
        ).data.items
        print(f"Total file sync runs for connector: {len(sync_runs)}")
        for item in sync_runs[:10]:
            print(f"File sync list item: {item.id} | {item.lifecycle_state} | {item.display_name}")

        fetched_sync = client.get_vector_store_connector_file_sync(file_sync_id).data
        print("Fetched file sync details:")
        print(f"id: {fetched_sync.id}")
        print(f"display_name: {fetched_sync.display_name}")
        print(f"lifecycle_state: {fetched_sync.lifecycle_state}")
        print(f"lifecycle_details: {fetched_sync.lifecycle_details}")
        print(f"trigger_type: {fetched_sync.trigger_type}")
        print(f"time_started: {fetched_sync.time_started}")
        print(f"time_ended: {fetched_sync.time_ended}")
        print(f"duration_in_seconds: {fetched_sync.duration_in_seconds}")

        if CANCEL_FILE_SYNC_IMMEDIATELY:
            client.cancel_vector_store_connector_file_sync(file_sync_id)
            print(f"Cancel request accepted for file sync: {file_sync_id}")
            fetched_sync = client.get_vector_store_connector_file_sync(file_sync_id).data
            print(f"Post-cancel lifecycle_state: {fetched_sync.lifecycle_state}")
        else:
            print(
                "Skipping file sync cancel. "
                "Set CANCEL_FILE_SYNC_IMMEDIATELY=True to demonstrate the cancel endpoint."
            )

        sync_logs = client.list_vector_store_connector_file_sync_ingestion_logs(
            file_sync_id,
            limit=10,
        ).data.items
        print(f"Returned sync-level ingestion log entries: {len(sync_logs)}")
        for entry in sync_logs:
            print(entry)

    # Step 12: Optional cleanup.
    if DELETE_CONNECTOR_AT_END:
        client.delete_vector_store_connector(connector_id)
        print(f"Delete request sent for {connector_id}")
    else:
        print("Skipping delete. Set DELETE_CONNECTOR_AT_END=True to delete connector.")

if __name__ == "__main__":
    main()
