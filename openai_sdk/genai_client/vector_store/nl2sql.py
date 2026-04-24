import json

import oci
from oci.base_client import BaseClient

# Learning goal:
# Call OCI Semantic Store NL2SQL endpoint using OCI BaseClient.
#
# How to run:
# uv run python genai_client/vector_store/nl2sql.py
#
# Safe experiments for students:
# 1. Change NATURAL_LANGUAGE_QUERY with your own business questions.
# 2. Move OCIDs/profile into environment variables before sharing.
# 3. Add safe retry strategy only when your endpoint supports idempotency.
#
# Note:
# This script depends on a valid OCI config profile and semantic store OCID.

INFERENCE_BASE_URL = "https://dev.inference.generativeai.us-ashburn-1.oci.oraclecloud.com"
API_VERSION = "20260325"
SEMANTIC_STORE_ID = (
    "ocid1.generativeaisemanticstore.oc1.iad."
    "zabaaaaa9k3m7qv2htr6cpx8wz1n4bdy5sj0fngq2v8xk3tq7mcp1zv6h2rd"
)
OCI_CONFIG_PROFILE = "oc1"
NATURAL_LANGUAGE_QUERY = "Give me last week order details ?"


def main() -> None:
    # Step 1: Build OCI signer and base client.
    oci_config = oci.config.from_file("~/.oci/config", OCI_CONFIG_PROFILE)
    signer = oci.auth.signers.SecurityTokenSigner(oci_config)
    client = BaseClient(
        service_endpoint=INFERENCE_BASE_URL,
        signer=signer,
        retry_strategy=None,
    )

    # Step 2: Prepare endpoint path and request body.
    resource_path = f"/{API_VERSION}/semanticStores/{SEMANTIC_STORE_ID}/actions/generateSqlFromNl"
    request_body = {
        "displayName": "displayName",
        "description": "description",
        "inputNaturalLanguageQuery": NATURAL_LANGUAGE_QUERY,
    }

    # Step 3: Send request and print parsed result.
    response = client.call_api(
        resource_path=resource_path,
        method="POST",
        header_params={"content-type": "application/json"},
        body=request_body,
    )

    print("HTTP status:", response.status)
    print("opc-request-id:", response.headers.get("opc-request-id"))

    parsed_data = response.data
    if isinstance(parsed_data, (bytes, str)):
        parsed_data = json.loads(parsed_data)
    print(json.dumps(parsed_data, indent=2))


if __name__ == "__main__":
    main()
