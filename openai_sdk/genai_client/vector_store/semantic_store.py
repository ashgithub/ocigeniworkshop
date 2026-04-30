"""What this file does:
Runs a semantic search directly against an existing vector store.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/semantic_store.py
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

VECTOR_STORE_ID = ""  # Set here, or create env var VECTOR_STORE_ID.
SEARCH_QUERY = "Summarize the business meaning of these documents."
MAX_RESULTS = 8

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve required vector store id.
    vector_store_id = VECTOR_STORE_ID or os.getenv("VECTOR_STORE_ID", "").strip()
    if not vector_store_id:
        raise ValueError(
            "Missing vector store id. Set VECTOR_STORE_ID constant in this file "
            "or create env var VECTOR_STORE_ID."
        )

    # Step 3: Run semantic search.
    result = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=SEARCH_QUERY,
        max_num_results=MAX_RESULTS,
        ranking_options={"ranker": "auto", "score_threshold": 0.0},
    )
    print("Semantic search results:")
    print(result)

if __name__ == "__main__":
    main()
