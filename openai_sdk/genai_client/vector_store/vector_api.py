""" What this file does:
Shows the main vector store lifecycle calls in one place:
1) Build the vector CRUD client and the search client.
2) Select an existing vector store id from `sandbox.yaml`.
3) Retrieve vector store metadata.
4) Update vector store name and metadata.
5) Run semantic search over the vector store.
6) List files already attached to the vector store.
7) Optionally attach and inspect one file.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Vector stores API reference: https://platform.openai.com/docs/api-reference/vector-stores
- Vector store files API reference: https://platform.openai.com/docs/api-reference/vector-stores-files
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Configure OCI credentials, project, compartment, and profile in `sandbox.yaml`.
- Set `oci.unstructured_vector_store_id` in `sandbox.yaml`.
- Optionally set `ATTACH_FILE_ID` to a Files API id that should be attached to the vector store.

How to run the file:
uv run openai_sdk/genai_client/vector_store/vector_api.py

Safe experiments:
1. Comment out the update call if you only want read/search behavior.
2. Update metadata keys and inspect retrieval output.
3. Attach one known file id to validate ingestion flow.
4. Keep a copy of the original vector store name if you are practicing updates.

Important sections:
1. Step 1: Build configured OpenAI clients.
2. Step 2: Resolve the vector store id.
3. Step 3: Retrieve vector store metadata.
4. Step 4: Update vector store name and metadata.
5. Step 5: Search the vector store and list attached files.
6. Step 6: Optional file attach and content inspection.
"""

# Vector store changes and file processing can take time, so this sample waits
# before searching after an update.

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

VECTOR_STORE_NAME = "workshop-vector-store"
VECTOR_STORE_DESCRIPTION = "Sample vector store created by vector_api.py"
SEARCH_QUERY = "Give me the key points from these documents."
UPLOAD_CLIENT_FILE = False

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    print("Step 1 - Building vector CRUD client and search client.")
    # The vector store client uses the 2023 endpoint for vector store CRUD operations.
    client: OpenAI = OpenAIClientProvider().oci_openai_vector_client
    # The OpenAI client is used for active retrieval and model-facing search operations.
    search_client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve the vector store id. The commented create block below is
    # useful when you want to create a fresh store and copy its id into sandbox.yaml.
    print("Step 2 - Resolving vector store id from sandbox.yaml.")
    # Create vector store. Use this commented block to get a new vector store id.
    # vector_store = client.vector_stores.create(
    #     name=VECTOR_STORE_NAME,
    #     description=VECTOR_STORE_DESCRIPTION,
    #     expires_after={"anchor": "last_active_at", "days": 30},
    #     metadata={"topic": "oci", "sample": "vector_api"},
    # )
    # print("Vector store created. Result:")
    # print(vector_store)
    # vector_store_id = vector_store.id
    vector_store_id = OpenAIClientProvider().oci_openai_unstructured_vector_store_id

    # Step 3: Retrieve vector store metadata.
    print(f"Step 3 - Retrieving vector store: {vector_store_id}")
    retrieve_result = client.vector_stores.retrieve(vector_store_id=vector_store_id)
    print(f"Vector store retrieved: {retrieve_result.name}")
    print(f"Vector store ID: {retrieve_result.id}")

    # Step 4: Update vector store name and metadata so beginners can see how
    # server-side metadata changes appear in API responses.
    # print("Step 4 - Updating vector store name and metadata.")
    # update_result = client.vector_stores.update(
    #     vector_store_id=vector_store_id,
    #     name=f"{VECTOR_STORE_NAME}-updated",
    #     metadata={"topic": "oci", "sample": "vector_api", "state": "updated", "update_id": str(datetime.now())},
    # )
    # print("Updated vector store on name:")
    # print(update_result.name)
    # print("Updated vector store on metadata:")
    # print(update_result.metadata)

    # # Wait for the changes to apply and for complete status on the vector store.
    # print("Waiting 30 seconds for vector store changes to settle before searching.")
    # time.sleep(30)
    # After the updates are applied, proceed with search.

    # Step 5: Search vector store and print the retrieved chunks.
    print(f"Step 5 - Searching vector store for: {SEARCH_QUERY}")
    search_results = search_client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=SEARCH_QUERY,
        max_num_results=10,
    )
    print(f"Search results for query: {SEARCH_QUERY}:")
    print("------------------------------- Semantic search results -------------------------------\n")
    for match in search_results.data:
        print(f"Data found on file {match.filename}")
        print(f"File attributes: {match.attributes}")
        print(f"Sample content snippet: {match.content[0].text[:100]}")
        print(f"Score on match: {match.score}\n\n")

    print("Step 5b - Listing files currently attached to the vector store.")
    file_list = search_client.vector_stores.files.list(vector_store_id=vector_store_id, limit=20)
    print("List of files on vector store:")
    for file in file_list.data:
        print(f"ID: {file.id}\nAttributes: {file.attributes}\nStatus: {file.status}\n")

    client_files_list = client.files.list(order="asc", limit=20)
    sample_file = client_files_list.data[0]

    print("Adding client file to the store:")
    print(f"File ID: {sample_file.id}")
    print(f"File name: {sample_file.filename}")

    # Step 6: Optional vector store file operations. This is separate from the
    # Files API upload step: here you attach an existing file id to a vector store.
    attach_file_id = sample_file.id
    if attach_file_id and UPLOAD_CLIENT_FILE:
        try:
            print(f"Step 6 - Attaching file id to vector store: {attach_file_id}")
            create_file_result = search_client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=attach_file_id,
                attributes={"category": "sample"},
            )
            print("created file:")
            print(create_file_result)
        except Exception:
            print("File already on store")

        retrieve_file_result = search_client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=attach_file_id,
        )
        print("Step 6b - Retrieving attached file metadata.")
        print(f"Retrieved file with id: {attach_file_id}")
        print(f"Data: {retrieve_file_result}")

        print("Step 6c - Fetching a content snippet for the attached file.")
        content_result = search_client.vector_stores.files.content(
            vector_store_id=vector_store_id,
            file_id=attach_file_id,
        )
        print("Content on file:\n")
        print(f"File: {content_result.file_name}")  # type: ignore
        print(f"File ID: {content_result.file_id}")  # type: ignore
        print(f"Content snippet: {content_result.content[0]['text'][:100]}\n")  # type: ignore
        
    else:
        print(
            "Skipping file attach flow. Set UPLOAD_CLIENT_FILE constant "
            "to inspect one existing Files API object."
        )

if __name__ == "__main__":
    main()
