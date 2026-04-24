from openai import OpenAI

from openai_sdk.openai_client_provider import OpenAIClientProvider

# Learning goal:
# Query a vector store using the file_search tool.
#
# How to run:
# uv run python genai_client/vector_store/file_search.py
#
# Safe experiments for students:
# 1. Replace VECTOR_STORE_ID with your own store.
# 2. Change USER_PROMPT to narrower retrieval questions.
# 3. Print full response object to inspect citations/metadata.
#
# Note:
# Set VECTOR_STORE_ID before running.

MODEL_ID = "gpt-4.1"
VECTOR_STORE_ID = "<vector_store_id>"
USER_PROMPT = "What are shapes of OCI GPU"


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Send query with file_search tool.
    response = client.responses.create(
        model=MODEL_ID,
        input=USER_PROMPT,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [VECTOR_STORE_ID],
            }
        ],
    )

    # Step 3: Print full response for inspection.
    print(response)


if __name__ == "__main__":
    main()
