"""What this file does:
Runs vector store connector APIs in one walkthrough:
1) Create connector
2) List connectors
3) Get connector details
4) Get connector stats
5) List ingestion logs
6) Optionally delete connector

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- OCI Generative AI control-plane docs (connector-related): internal GA guide
  https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Set `VECTOR_STORE_ID` constant or env var `VECTOR_STORE_ID`.
- Ensure object storage bucket values exist in `sandbox.yaml` (or env fallbacks).

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_store_connector.py

Safe experiments:
1. Run with `DELETE_CONNECTOR_AT_END=False` to inspect created connector state.
2. Adjust `VECTOR_OS_PREFIXES` to scope ingestion.
3. Review logs output after ingestion windows.

Important sections:
1. Step 1: Build OCI control-plane client.
2. Step 2: Resolve runtime values.
3. Step 3-8: Execute connector lifecycle operations.
"""

import os
import sys
import oci

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

VECTOR_STORE_ID = ""  # Set here, or create env var VECTOR_STORE_ID.
VECTOR_OS_PREFIXES = []  # Optional object storage prefixes.
CONNECTOR_DISPLAY_NAME = "workshop-vector-connector"
CONNECTOR_DESCRIPTION = "Connector sample created by vector_store_connector.py"
DELETE_CONNECTOR_AT_END = False

def main():
    # Step 1: Build the OCI control-plane client from OpenAIClientProvider.
    provider = OpenAIClientProvider()
    client, compartment_id = provider.build_oci_generative_ai_control_plane_client()

    # Step 2: Resolve required values.
    vector_store_id = VECTOR_STORE_ID or os.getenv("VECTOR_STORE_ID", "").strip()
    if not vector_store_id:
        raise ValueError(
            "Missing vector store id. Set VECTOR_STORE_ID constant in this file "
            "or create env var VECTOR_STORE_ID."
        )

    # Prefer sandbox.yaml bucket values for beginner setup.
    namespace = provider.get_sandbox_value("bucket", "namespace", "") or ""
    bucket_name = provider.get_sandbox_value("bucket", "bucketName", "") or ""

    # If missing in sandbox config, allow env overrides.
    namespace = namespace or os.getenv("VECTOR_OS_NAMESPACE", "").strip()
    bucket_name = bucket_name or os.getenv("VECTOR_OS_BUCKET", "").strip()
    if not namespace or not bucket_name:
        raise ValueError(
            "Missing object storage namespace/bucket. "
            "Use sandbox.yaml -> bucket.namespace and bucket.bucketName, "
            "or create env vars VECTOR_OS_NAMESPACE and VECTOR_OS_BUCKET."
        )

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
                    prefix_list=VECTOR_OS_PREFIXES,
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

    # Step 5: Get connector.
    fetched = client.get_vector_store_connector(connector_id).data
    print(fetched)

    # Step 6: Get connector stats.
    stats = client.get_vector_store_connector_stats(connector_id).data
    print(stats)

    # Step 7: List ingestion logs.
    logs = client.list_vector_store_connector_ingestion_logs(connector_id, limit=10).data.items
    print(f"Returned log entries: {len(logs)}")

    # Step 8: Optional cleanup.
    if DELETE_CONNECTOR_AT_END:
        client.delete_vector_store_connector(connector_id)
        print(f"Delete request sent for {connector_id}")
    else:
        print("Skipping delete. Set DELETE_CONNECTOR_AT_END=True to delete connector.")

if __name__ == "__main__":
    main()
