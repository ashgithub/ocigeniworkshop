"""Semantic search-style workflow using vector stores.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/semantic_store.py

Required environment variable:
- VECTOR_STORE_ID: existing vector store id

Optional environment variables:
- VECTOR_SEMANTIC_QUERY
- VECTOR_SEMANTIC_LIMIT
"""

from __future__ import annotations

try:
    from .vector_genai_client import get_client, get_env, print_section, require_env
except ImportError:
    from vector_genai_client import get_client, get_env, print_section, require_env


DEFAULT_QUERY = "Summarize the business meaning of these documents."


def main() -> None:
    client = get_client()
    vector_store_id = require_env("VECTOR_STORE_ID")
    query = get_env("VECTOR_SEMANTIC_QUERY", DEFAULT_QUERY)

    limit_raw = get_env("VECTOR_SEMANTIC_LIMIT", "8")
    limit = int(limit_raw)

    print_section("Semantic Search")
    result = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
        max_num_results=limit,
        ranking_options={"ranker": "auto", "score_threshold": 0.0},
    )
    print(result)


if __name__ == "__main__":
    main()
