"""Vector store CRUD sample.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_api.py

Optional environment variables:
- VECTOR_SAMPLE_FILE_ID: file id to attach to the created vector store
- VECTOR_SEARCH_QUERY: query for vector store search
- VECTOR_DELETE_VECTOR_STORE: set to true to delete created store at end
"""

from __future__ import annotations

try:
    from .vector_genai_client import as_bool, get_client, get_env, print_section
except ImportError:
    from vector_genai_client import as_bool, get_client, get_env, print_section


DEFAULT_QUERY = "Give me the key points from these documents."


def main() -> None:
    client = get_client()
    query = get_env("VECTOR_SEARCH_QUERY", DEFAULT_QUERY)
    sample_file_id = get_env("VECTOR_SAMPLE_FILE_ID")

    print_section("Create Vector Store")
    vector_store = client.vector_stores.create(
        name="workshop-vector-store",
        description="Sample vector store created by vector_api.py",
        expires_after={"anchor": "last_active_at", "days": 30},
        metadata={"topic": "oci", "sample": "vector_api"},
    )
    print(vector_store)

    vector_store_id = vector_store.id

    print_section("Retrieve Vector Store")
    retrieve_result = client.vector_stores.retrieve(vector_store_id=vector_store_id)
    print(retrieve_result)

    print_section("Update Vector Store")
    update_result = client.vector_stores.update(
        vector_store_id=vector_store_id,
        name="workshop-vector-store-updated",
        metadata={"topic": "oci", "sample": "vector_api", "state": "updated"},
    )
    print(update_result)

    print_section("Search Vector Store")
    query="example"
    search_results = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
        max_num_results=10,
    )
    print(search_results)

    if sample_file_id:
        print_section("Attach File to Vector Store")
        create_file_result = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=sample_file_id,
            attributes={"category": "sample"},
        )
        print(create_file_result)

        print_section("List Vector Store Files")
        files_result = client.vector_stores.files.list(vector_store_id=vector_store_id, limit=20)
        print(files_result)

        print_section("Retrieve Vector Store File")
        retrieve_file_result = client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=sample_file_id,
        )
        print(retrieve_file_result)

        print_section("Retrieve Vector Store File Content")
        content_result = client.vector_stores.files.content(
            vector_store_id=vector_store_id,
            file_id=sample_file_id,
        )
        print(content_result)
    else:
        print("Skipping vector store file operations: set VECTOR_SAMPLE_FILE_ID.")

    if as_bool("VECTOR_DELETE_VECTOR_STORE", default=False):
        print_section("Delete Vector Store")
        delete_result = client.vector_stores.delete(vector_store_id=vector_store_id)
        print(delete_result)
    else:
        print("Keeping vector store for inspection. Set VECTOR_DELETE_VECTOR_STORE=true to delete it.")


if __name__ == "__main__":
    main()
