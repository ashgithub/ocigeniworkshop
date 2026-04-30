"""What this file does:
Shows vector store create/retrieve/update/search and optional file attach flow.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_api.py
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

VECTOR_STORE_NAME = "workshop-vector-store"
VECTOR_STORE_DESCRIPTION = "Sample vector store created by vector_api.py"
SEARCH_QUERY = "Give me the key points from these documents."
ATTACH_FILE_ID = ""  # Set file id here, or create env var VECTOR_SAMPLE_FILE_ID.
DELETE_VECTOR_STORE_AT_END = False  # Set True if you want cleanup in same run.

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Create vector store.
    vector_store = client.vector_stores.create(
        name=VECTOR_STORE_NAME,
        description=VECTOR_STORE_DESCRIPTION,
        expires_after={"anchor": "last_active_at", "days": 30},
        metadata={"topic": "oci", "sample": "vector_api"},
    )
    print("Vector store created. Result:")
    print(vector_store)
    vector_store_id = vector_store.id

    # Step 3: Retrieve vector store.
    retrieve_result = client.vector_stores.retrieve(vector_store_id=vector_store_id)
    print("Vector store retrieved:")
    print(retrieve_result)

    # Step 4: Update vector store.
    update_result = client.vector_stores.update(
        vector_store_id=vector_store_id,
        name=f"{VECTOR_STORE_NAME}-updated",
        metadata={"topic": "oci", "sample": "vector_api", "state": "updated"},
    )
    print("Updated vector store:")
    print(update_result)

    # Step 5: Search vector store.
    search_results = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=SEARCH_QUERY,
        max_num_results=10,
    )
    print(f"Search results for query: {SEARCH_QUERY}:")
    print(search_results)

    # Step 6: Optional vector-store file operations.
    attach_file_id = ATTACH_FILE_ID or os.getenv("VECTOR_SAMPLE_FILE_ID", "").strip()
    if attach_file_id:
        create_file_result = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=attach_file_id,
            attributes={"category": "sample"},
        )
        print("created file:")
        print(create_file_result)

        file_list = client.vector_stores.files.list(vector_store_id=vector_store_id, limit=20)
        print("List of files on vector store:")
        print(file_list)

        retrieve_file_result = client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=attach_file_id,
        )
        print(f"Retrieved file with id: {attach_file_id}")
        print(retrieve_file_result)

        content_result = client.vector_stores.files.content(
            vector_store_id=vector_store_id,
            file_id=attach_file_id,
        )
        print("Content on file:")
        print(content_result)
    else:
        print(
            "Skipping file attach flow. Set ATTACH_FILE_ID constant "
            "or create env var VECTOR_SAMPLE_FILE_ID."
        )

    # Step 7: Optional cleanup.
    if DELETE_VECTOR_STORE_AT_END:
        delete_result = client.vector_stores.delete(vector_store_id=vector_store_id)
        print(delete_result)
    else:
        print("Keeping vector store for inspection. Set DELETE_VECTOR_STORE_AT_END=True to delete it.")

if __name__ == "__main__":
    main()
