"""What this file does:
Shows end-to-end vector store lifecycle:
1) Create vector store
2) Retrieve vector store
3) Update vector store metadata/name
4) Run semantic search
5) Optionally attach and inspect files
6) Optionally delete vector store

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Vector stores API reference: https://platform.openai.com/docs/api-reference/vector-stores
- Vector store files API reference: https://platform.openai.com/docs/api-reference/vector-stores-files
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Optionally provide `ATTACH_FILE_ID` or env var `VECTOR_SAMPLE_FILE_ID`.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_api.py

Safe experiments:
1. Keep `DELETE_VECTOR_STORE_AT_END=False` while learning.
2. Update metadata keys and inspect retrieval output.
3. Attach one known file id to validate ingestion flow.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2-5: Create/retrieve/update/search vector store.
3. Step 6-7: Optional file attach and cleanup.
"""

# this kind of files requires execution time to wait since the job of creating vector store and file processing is long

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

VECTOR_STORE_NAME = "workshop-vector-store"
VECTOR_STORE_DESCRIPTION = "Sample vector store created by vector_api.py"
SEARCH_QUERY = "Give me the key points from these documents."
ATTACH_FILE_ID = "file-ord-459fa3aa-6e29-46ab-a1ce-e0e8a7683873"  # Set file id here, or create env var VECTOR_SAMPLE_FILE_ID.
DELETE_VECTOR_STORE_AT_END = True  # Set True if you want cleanup in same run.

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    client: OpenAI = OpenAIClientProvider().oci_openai_vector_client
    search_client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Create vector store.
    # vector_store = client.vector_stores.create(
    #     name=VECTOR_STORE_NAME,
    #     description=VECTOR_STORE_DESCRIPTION,
    #     expires_after={"anchor": "last_active_at", "days": 30},
    #     metadata={"topic": "oci", "sample": "vector_api"},
    # )
    # print("Vector store created. Result:")
    # print(vector_store)
    # vector_store_id = vector_store.id
    vector_store_id = "vs_ord_tgcknsijp4c5zcc64s37ftoddmegpnquxepj7zkmvyhfdpfi"

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
    search_results = search_client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=SEARCH_QUERY,
        max_num_results=10,
    )
    print(f"Search results for query: {SEARCH_QUERY}:")
    print(search_results)

    # Step 6: Optional vector-store file operations.
    attach_file_id = ATTACH_FILE_ID or os.getenv("VECTOR_SAMPLE_FILE_ID", "").strip()
    if attach_file_id:
        try:
            create_file_result = search_client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=attach_file_id,
                attributes={"category": "sample"},
            )
            print("created file:")
            print(create_file_result)
        except Exception:
            print("File already on store")

        file_list = search_client.vector_stores.files.list(vector_store_id=vector_store_id, limit=20)
        print("List of files on vector store:")
        print(file_list)

        retrieve_file_result = search_client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=attach_file_id,
        )
        print(f"Retrieved file with id: {attach_file_id}")
        print(retrieve_file_result)

        content_result = search_client.vector_stores.files.content(
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
