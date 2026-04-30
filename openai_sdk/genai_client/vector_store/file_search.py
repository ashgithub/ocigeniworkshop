"""File search sample using a vector store.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/file_search.py

Required environment variable:
- VECTOR_STORE_ID: vector store id used by the file_search tool

Optional environment variable:
- VECTOR_SEARCH_PROMPT: user prompt for search (default provided)
"""

from __future__ import annotations

try:
    from .vector_genai_client import get_client, get_env, print_section, require_env
except ImportError:
    from vector_genai_client import get_client, get_env, print_section, require_env


DEFAULT_PROMPT = "What does this knowledge base say about OCI GPU shapes?"


def main() -> None:
    client = get_client()
    vector_store_id = require_env("VECTOR_STORE_ID")
    prompt = get_env("VECTOR_SEARCH_PROMPT", DEFAULT_PROMPT)
    prompt="example"

    print_section("Responses API with file_search")
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
