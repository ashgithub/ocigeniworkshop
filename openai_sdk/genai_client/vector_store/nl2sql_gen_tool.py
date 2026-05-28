""" What this file does:
Generates SQL from a natural-language question using an existing semantic store:
1) Load the structured semantic store id and NL2SQL endpoint from `sandbox.yaml`.
2) Submit a `generateSqlFromNl` REST request.
3) Print the full JSON response and extracted SQL.
4) Ask for human approval before executing the generated SQL.
5) Print a small table of database results when execution is approved.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Create the semantic store and enrichment job in OCI Console before running this script.
- Configure `oci.structured_vector_store_id` in `sandbox.yaml`.
- Configure database connection values in `sandbox.yaml` if you plan to execute the generated SQL.
- Confirm `NL2SQL_ENDPOINT` in `openai_client_provider.py` points to your inference endpoint.

How to run the file:
uv run openai_sdk/genai_client/vector_store/nl2sql_gen_tool.py

Safe experiments:
1. Start with read-only questions that produce SELECT statements.
2. Review the printed SQL carefully before approving execution.
3. Lower `MAX_ROWS` while validating a new semantic store or database connection.

Important sections:
1. Step 1: Load provider configuration and auth.
2. Step 2: Build REST headers for the NL2SQL endpoint.
3. Step 3: Submit the natural-language question.
4. Step 4: Extract and print the generated SQL.
5. Step 5: Request explicit approval before database execution.
6. Step 6: Execute SQL and print a compact result table.
"""

import json
import os
import sys

import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

# NATURAL_LANGUAGE_QUERY = "Select the tables from the current schema"
NATURAL_LANGUAGE_QUERY = "List the available energy sources and their providers use the schema provided"
# NATURAL_LANGUAGE_QUERY = "For each customer, show the energy type and provider used in each reading period"
# NATURAL_LANGUAGE_QUERY = "List only commercial customers and their energy usage"
# NATURAL_LANGUAGE_QUERY = "Show total kWh used by energy source"
REQUEST_TIMEOUT_SECONDS = 120.0
MAX_ROWS = 20

def print_table(columns: list[str], rows: list[tuple]) -> None:
    """Print database rows in aligned columns for quick workshop inspection."""
    if not rows:
        print("No rows returned.")
        return

    # Calculate display widths from headers and values so the output is readable
    # without requiring a spreadsheet or database client.
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
    # Step 1: Load provider-managed configuration, endpoint, semantic store id,
    # database helpers, and OCI user auth.
    print("Step 1 - Loading OCI provider, semantic store id, endpoint, and auth.")
    provider = OpenAIClientProvider()
    semantic_store_id = provider.oci_openai_structured_vector_store_id
    question = NATURAL_LANGUAGE_QUERY
    endpoint = provider.oci_openai_nl2sql_endpoint.rstrip("/")
    auth = provider.get_raw_user_auth()

    # Step 2: Build the REST headers required by OCI and the OpenAI-compatible
    # project routing layer.
    print("Step 2 - Building request headers.")
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "OpenAI-Project": provider.oci_openai_project,
        "opc-compartment-id": provider.oci_compartment_id,
        "compartment-id": provider.oci_compartment_id,
    }

    # Step 3: Submit the natural-language question to the semantic store.
    print("Step 3 - Requesting NL2SQL job.")
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
        payload: dict = response.json()

    # Step 4: Print the complete service response first, then the SQL string
    # extracted from the common response location.
    print("Generated SQL response:")
    print(json.dumps(payload, indent=2))

    generated_sql = payload.get("jobOutput", {}).get("content", "").strip()
    
    print("\nExtracted SQL:")
    print(generated_sql)

    # Step 5: Require explicit user approval before sending generated SQL to
    # the database. This keeps the demo safe for beginners.
    user_approval = input("Execute generated query? [y/N]")

    if user_approval == "y":
        # Step 6: Execute the approved SQL and print only the first MAX_ROWS
        # rows so terminal output stays readable.
        print("\nStep 6 - Executing SQL against the database.")
        with provider.connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(generated_sql)
                columns = [column[0] for column in cursor.description]  # type: ignore
                rows = cursor.fetchmany(MAX_ROWS)

        print(f"\nQuery results (first {MAX_ROWS} rows):")
        print_table(columns, rows)  # type: ignore
    else:
        print("Skipping generated SQL execution.")


if __name__ == "__main__":
    main()
