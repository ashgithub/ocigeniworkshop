"""Generate SQL-style output from indexed documentation using file_search.

This is a practical replacement for raw SQL-generation endpoint experiments:
we ask a model to synthesize SQL from documents indexed in a vector store.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/sql_invocation.py

Required environment variable:
- VECTOR_STORE_ID: vector store containing schema/table documentation

Optional environment variables:
- VECTOR_SQL_REQUEST: natural-language request to convert into SQL
"""

from __future__ import annotations

try:
    from .vector_genai_client import get_client, get_env, print_section, require_env
except ImportError:
    from vector_genai_client import get_client, get_env, print_section, require_env


DEFAULT_SQL_REQUEST = "Generate SQL to return last week's order details."


def main() -> None:
    client = get_client()
    vector_store_id = require_env("VECTOR_STORE_ID")
    nl_request = get_env("VECTOR_SQL_REQUEST", DEFAULT_SQL_REQUEST)

    prompt = (
        "You are a SQL assistant. Use the retrieved documents as the source of truth. "
        "Return only SQL unless clarification is required. Request: "
        f"{nl_request}"
    )

    print_section("Generate SQL from Indexed Docs")
    response = client.responses.create(
        model="openai.gpt-5.2",
        input=prompt,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
            }
        ],
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
