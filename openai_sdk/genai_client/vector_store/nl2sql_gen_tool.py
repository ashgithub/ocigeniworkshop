"""Generate SQL from a natural-language question using an existing semantic store.

Run from repo root:
uv run openai_sdk/genai_client/vector_store/nl2sql_gen_tool.py

Or pass the semantic store ID and question directly:
uv run openai_sdk/genai_client/vector_store/nl2sql_gen_tool.py <semantic-store-ocid> "List my tables"

Before running:
1. Create the semantic store and enrichment job in OCI Console.
2. Paste the semantic store OCID into SEMANTIC_STORE_ID, or set SEMANTIC_STORE_ID.
3. Confirm NL2SQL_ENDPOINT points to your inference endpoint.
"""

import json
import os
import sys

import httpx
import oracledb
from oci_genai_auth import OciUserPrincipalAuth

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider


# Edit these values for your test.
NL2SQL_API_VERSION = "20260325"
NL2SQL_ENDPOINT = "https://inference.generativeai.us-phoenix-1.oci.oraclecloud.com/20260325"
# SEMANTIC_STORE_ID = "ocid1.generativeaisemanticstore.oc1.phx.amaaaaaaghwivzaa4r3cg2ebniryy7tgq7mfrkyjdmpmushpncla2mdc4gza"
SEMANTIC_STORE_ID = "ocid1.generativeaisemanticstore.oc1.phx.amaaaaaaghwivzaawbxwlrwvwfvooj2ttgwscxtcfckrki6st7wd7c2jeaoq"
# NATURAL_LANGUAGE_QUERY = "Give me 5 DB table names that you could find there"
NATURAL_LANGUAGE_QUERY = "Explain the data on WL_CALLS table"
REQUEST_TIMEOUT_SECONDS = 120.0
MAX_ROWS = 20

def print_table(columns: list[str], rows: list[tuple]) -> None:
    if not rows:
        print("No rows returned.")
        return

    widths = [len(column) for column in columns]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))

    row_format = " | ".join(f"{{:<{width}}}" for width in widths)
    separator = "-+-".join("-" * width for width in widths)

    print(row_format.format(*columns))
    print(separator)
    for row in rows:
        print(row_format.format(*[str(value) for value in row]))


def main() -> None:
    provider = OpenAIClientProvider()
    semantic_store_id = SEMANTIC_STORE_ID
    question = NATURAL_LANGUAGE_QUERY
    endpoint = NL2SQL_ENDPOINT.rstrip("/")

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "OpenAI-Project": provider.oci_openai_project,
        "opc-compartment-id": provider.oci_compartment_id,
        "compartment-id": provider.oci_compartment_id,
    }

    auth = OciUserPrincipalAuth(
        config_file=os.path.expanduser(provider.oci_openai_config_file),
        profile_name=provider.oci_openai_profile,
    )

    print(f"Using endpoint: {endpoint}")
    print(f"Using OCI profile: {provider.oci_openai_profile}")
    print(f"Using semantic store id: {semantic_store_id}")
    print(f"Question: {question}")

    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, auth=auth) as client:
        url = f"{endpoint.rstrip('/')}/semanticStores/{semantic_store_id}/actions/generateSqlFromNl"
        response = client.post(
            url,
            headers=headers,
            json={
                "displayName": "nl2sql-request",
                "description": "Generate SQL from natural language",
                "inputNaturalLanguageQuery": question,
            },
        )
        response.raise_for_status()
        payload:dict = response.json()

    print("Generated SQL response:")
    print(json.dumps(payload, indent=2))

    generated_sql = payload.get("jobOutput",{}).get("content","").strip()
    
    print("\nExtracted SQL:")
    print(generated_sql)

    user_approval = input("Execute generated query? [y/N]")

    if user_approval == 'y':
        print("\nExecuting SQL against the database...")
        with provider.connect_db() as connection:
            with connection.cursor() as cursor:
                    cursor.execute(generated_sql)
                    columns = [column[0] for column in cursor.description] #type:ignore
                    rows = cursor.fetchmany(MAX_ROWS)

        print(f"\nQuery results (first {MAX_ROWS} rows):")
        print_table(columns, rows) #type:ignore
    else:
        print("Skippin generated SQL execution")


if __name__ == "__main__":
    main()


# {
#   "mcpServers": {
#     "nl2sql_sales_database": {
#       "description": "NL2SQL MCP server for the sales database semantic store. Translates natural language to SQL and delegates execution to sales_database_mcp_server.",
#       "command": "/opt/homebrew/bin/npx",
#       "args": [
#         "-y",
#         "mcp-remote",
#         "https://genai.oci.{region-identifier}.oraclecloud.com/nl2sql/toolchain",
#         "--allow-http"
#       ],
#       "transport": "streamable-http"
#     }
#   }
# }