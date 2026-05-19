""" What this file does:
Demonstrates direct semantic search against an existing vector store:
1) Read the vector store id from the workshop configuration.
2) Submit a search query without generating a model answer.
3) Print matching files, attributes, snippets, and scores.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Vector stores API reference: https://platform.openai.com/docs/api-reference/vector-stores
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Configure OCI credentials, project, compartment, and profile in `sandbox.yaml`.
- Set `oci.unstructured_vector_store_id` in `sandbox.yaml` to the vector store you want to search.

How to run the file:
uv run openai_sdk/genai_client/vector_store/semantic_store.py

Safe experiments:
1. Tune `MAX_RESULTS` to compare precision vs. recall.
2. Change `ranking_options` threshold to filter weaker matches.
3. Test several queries and compare returned chunks.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Resolve vector store id.
3. Step 3: Execute semantic search.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

SEARCH_QUERY = "Summarize the business meaning of these documents."
MAX_RESULTS = 8

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    print("Step 1 - Building OCI OpenAI client.")
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve required vector store id. Semantic search needs an
    # already-created vector store with processed files.
    print("Step 2 - Resolving vector store id from sandbox.yaml.")
    vector_store_id = OpenAIClientProvider().oci_openai_unstructured_vector_store_id

    # Step 3: Run semantic search. This returns retrieved chunks directly
    # instead of asking a model to turn them into an answer.
    print(f"Step 3 - Searching vector store {vector_store_id} for: {SEARCH_QUERY}")
    result = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=SEARCH_QUERY,
        max_num_results=MAX_RESULTS,
        ranking_options={"ranker": "auto", "score_threshold": 0.0},
    )
    print("------------------------------- Semantic search results -------------------------------\n")
    for match in result.data:
        print(f"Data found on file {match.filename}")
        print(f"File attributes: {match.attributes}")
        print(f"Sample content snippet: {match.content[0].text[:100]}")
        print(f"Score on match: {match.score}\n")

if __name__ == "__main__":
    main()
