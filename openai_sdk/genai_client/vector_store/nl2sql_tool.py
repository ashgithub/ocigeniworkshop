"""What this file does:
Shows NL2SQL in two beginner-friendly sections:
1) Semantic store setup (create/get)
2) SQL generation from natural language

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/nl2sql_tool.py

Important:
- Client/auth initialization is centralized through `OpenAIClientProvider`.
- The flow is "create resource first, then use it."
"""

import json
import os
import sys
from typing import Any

from oci.retry import DEFAULT_RETRY_STRATEGY

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

# ---------------------------
# Section 1 - User-editable settings
# ---------------------------
SEMANTIC_STORE_API_VERSION = "20231130"
NL2SQL_API_VERSION = "20260325"

SEMANTIC_STORE_HOST = "https://dev.generativeai.us-ashburn-1.oci.oraclecloud.com"
INFERENCE_HOST = "https://dev.inference.generativeai.us-ashburn-1.oci.oraclecloud.com"

NATURAL_LANGUAGE_QUERY = "Give me last week order details."

# If you already have a semantic store, set it here (or use env var SEMANTIC_STORE_ID).
SEMANTIC_STORE_ID = ""

# Set True only if you want this script to create a semantic store when id is missing.
CREATE_SEMANTIC_STORE_IF_MISSING = False

# Required only when CREATE_SEMANTIC_STORE_IF_MISSING = True
SEMANTIC_STORE_DISPLAY_NAME = "WorkshopSemanticStore"
SEMANTIC_STORE_DESCRIPTION = "Semantic store for NL2SQL learning example"
QUERYING_CONNECTION_ID = ""
ENRICHMENT_CONNECTION_ID = ""
SCHEMA_NAME = "ADMIN"


# ---------------------------
# Section 2 - Shared helpers
# ---------------------------
def parse_response_data(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return data
    if isinstance(data, (bytes, str)):
        return json.loads(data)
    return {}


# ---------------------------
# Section 3 - Semantic store operations
# ---------------------------
def create_semantic_store(client, compartment_id: str) -> str:
    querying_connection_id = QUERYING_CONNECTION_ID or os.getenv("QUERYING_CONNECTION_ID", "").strip()
    enrichment_connection_id = ENRICHMENT_CONNECTION_ID or os.getenv("ENRICHMENT_CONNECTION_ID", "").strip()

    if not querying_connection_id or not enrichment_connection_id:
        raise ValueError(
            "To create a semantic store, set QUERYING_CONNECTION_ID and ENRICHMENT_CONNECTION_ID "
            "in this file or as env vars."
        )

    body = {
        "displayName": SEMANTIC_STORE_DISPLAY_NAME,
        "description": SEMANTIC_STORE_DESCRIPTION,
        "freeformTags": {},
        "definedTags": {},
        "dataSource": {
            "queryingConnectionId": querying_connection_id,
            "enrichmentConnectionId": enrichment_connection_id,
            "connectionType": "DATABASE_TOOLS_CONNECTION",
        },
        "refreshSchedule": {"type": "ON_CREATE"},
        "compartmentId": compartment_id,
        "schemas": {
            "connectionType": "DATABASE_TOOLS_CONNECTION",
            "schemas": [{"name": SCHEMA_NAME}],
        },
    }

    response = client.base_client.call_api(
        resource_path=f"/{SEMANTIC_STORE_API_VERSION}/semanticStores",
        method="POST",
        header_params={"content-type": "application/json"},
        body=body,
    )
    payload = parse_response_data(response.data)
    semantic_store_id = payload.get("id", "").strip()
    if not semantic_store_id:
        raise ValueError(f"Semantic store creation did not return an id. Response: {payload}")
    print(f"Semantic store created: {semantic_store_id}")
    return semantic_store_id


def get_semantic_store(client, semantic_store_id: str) -> dict[str, Any]:
    response = client.base_client.call_api(
        resource_path=f"/{SEMANTIC_STORE_API_VERSION}/semanticStores/{semantic_store_id}",
        method="GET",
        retry_strategy=DEFAULT_RETRY_STRATEGY, #type:ignore
    )
    return parse_response_data(response.data)


# ---------------------------
# Section 4 - SQL generation operation
# ---------------------------
def generate_sql_from_nl(client, semantic_store_id: str, nl_query: str) -> dict[str, Any]:
    response = client.base_client.call_api(
        resource_path=f"/{NL2SQL_API_VERSION}/semanticStores/{semantic_store_id}/actions/generateSqlFromNl",
        method="POST",
        header_params={"content-type": "application/json"},
        body={
            "displayName": "nl2sql-request",
            "description": "Generate SQL from natural language",
            "inputNaturalLanguageQuery": nl_query,
        },
    )
    return parse_response_data(response.data)


def main() -> None:
    # Step 1: Build provider once (centralized init from openai_client_provider.py).
    provider = OpenAIClientProvider()

    # Step 2: Build OCI generated clients (they initialize BaseClient safely for us).
    semantic_client, compartment_id = provider.build_oci_generative_ai_control_plane_client()
    inference_client = provider.build_oci_generative_ai_inference_client(service_endpoint=INFERENCE_HOST)

    # Step 3: Resolve semantic store id; create first if requested.
    semantic_store_id = SEMANTIC_STORE_ID or os.getenv("SEMANTIC_STORE_ID", "").strip()
    if not semantic_store_id:
        if not CREATE_SEMANTIC_STORE_IF_MISSING:
            raise ValueError(
                "Missing semantic store id. Either set SEMANTIC_STORE_ID (or env var SEMANTIC_STORE_ID), "
                "or set CREATE_SEMANTIC_STORE_IF_MISSING=True and provide connection ids."
            )
        semantic_store_id = create_semantic_store(semantic_client, compartment_id)

    # Step 4: Verify semantic store exists before using it.
    semantic_store = get_semantic_store(semantic_client, semantic_store_id)
    print(f"Semantic store ready: {semantic_store.get('id', semantic_store_id)}")

    # Step 5: Generate SQL using the semantic store.
    sql_payload = generate_sql_from_nl(inference_client, semantic_store_id, NATURAL_LANGUAGE_QUERY)
    print("Generated SQL response:")
    print(json.dumps(sql_payload, indent=2))


if __name__ == "__main__":
    main()
