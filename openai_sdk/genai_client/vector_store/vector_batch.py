""" What this file does:
Shows the complete vector store file batch flow in one standalone script:
1) Upload one or more local files with the Files API
2) Create a vector store file batch from the uploaded file ids
3) Retrieve batch status
4) Poll until the batch reaches a terminal state
5) List files in batch
6) Optionally cancel the batch right after creation
7) Optionally remove uploaded files from the vector store and Files API

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Files API reference: https://platform.openai.com/docs/api-reference/files
- Vector store file batches API reference: https://platform.openai.com/docs/api-reference/vector-stores-file-batches
- File Search guide: https://platform.openai.com/docs/guides/tools-file-search/
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Configure OCI credentials, project, compartment, and profile in `sandbox.yaml`.
- Set a valid `oci.unstructured_vector_store_id` in `sandbox.yaml`.
- Point `LOCAL_FILE_PATHS` to one or more local files on your machine.

How to run the file:
uv run openai_sdk/genai_client/vector_store/vector_batch.py

Safe experiments:
1. Start with one small PDF or text file.
2. Keep cleanup flags as `False` until you validate the batch flow.
3. Use attributes to tag files for later filtering and debugging.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Upload local files and collect `file_id` values.
3. Step 3-7: Create/retrieve/poll/list/cancel batch flow.
4. Step 8-9: Optional cleanup of vector store files and uploaded files.
"""

from openai import OpenAI
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

LOCAL_FILE_PATHS = [
    "./openai_sdk/output/sample_doc.pdf",
]  # Replace with one or more local file paths.

POLL_INTERVAL_SECONDS = 5
CANCEL_BATCH_IMMEDIATELY = False

def cleanup_vector_store_files(client: OpenAI, vector_store_id: str, file_ids: list[str]) -> None:
    """Detach uploaded files from the vector store while keeping the Files API objects."""
    for file_id in file_ids:
        try:
            delete_result = client.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id,
            )
            print(f"Removed file from vector store: {file_id}")
            print(delete_result)
        except Exception as exc:
            print(f"Could not remove file {file_id} from vector store: {exc}")


def cleanup_uploaded_files(client: OpenAI, file_ids: list[str]) -> None:
    """Delete uploaded Files API objects after the vector store demo is finished."""
    for file_id in file_ids:
        try:
            delete_result = client.files.delete(file_id=file_id)
            print(f"Deleted uploaded file object: {file_id}")
            print(delete_result)
        except Exception as exc:
            print(f"Could not delete uploaded file {file_id}: {exc}")


def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    print("Step 1 - Building OCI OpenAI client.")
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve required vector store input. File batches must target an
    # existing vector store.
    print("Step 2 - Resolving vector store id from sandbox.yaml.")
    vector_store_id = OpenAIClientProvider().oci_openai_unstructured_vector_store_id
    print(f"Using vector store id: {vector_store_id}")

    # Step 3: Upload local files and collect the returned file ids. The batch
    # endpoint receives file ids, not local paths.
    print("Step 3 - Uploading local files for batch ingestion.")
    uploaded_file_ids: list[str] = []

    for file_path in LOCAL_FILE_PATHS:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found: {file_path}")

        with open(file_path, "rb") as file_handle:
            uploaded_file = client.files.create(file=file_handle, purpose="user_data")

        print(f"Uploaded file from local path: {file_path}")
        print(f"Returned file id: {uploaded_file.id}\n")
        uploaded_file_ids.append(uploaded_file.id)

    print("File ids created by the Files API:")
    print(uploaded_file_ids)

    # Step 4: Create vector store file batch using the uploaded file ids.
    print("Step 4 - Creating vector store file batch.")
    batch = client.vector_stores.file_batches.create(
        vector_store_id=vector_store_id,
        file_ids=uploaded_file_ids,
        attributes={"category": "sample_py_code_batch"},
        chunking_strategy={"type": "auto"},
    )
    print("Created vector store file batch:")
    print(batch)
    print()
    batch_id = batch.id

    # Step 5: Retrieve file batch right after creation to confirm the server
    # accepted the request and returned a batch id.
    print(f"Step 5 - Retrieving batch after creation: {batch_id}")
    retrieve_result = client.vector_stores.file_batches.retrieve(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
    )
    print("Retrieved batch after creation:")
    print(retrieve_result)
    print()

    # Step 6: Optionally cancel right after creation to demonstrate cancel flow.
    print("Step 6 - Checking whether immediate cancel is enabled.")
    if CANCEL_BATCH_IMMEDIATELY:
        cancel_result = client.vector_stores.file_batches.cancel(
            vector_store_id=vector_store_id,
            batch_id=batch_id,
        )
        print("Cancel request sent for batch:")
        print(cancel_result)
        print()
    else:
        print(
            "Skipping immediate cancel. Set CANCEL_BATCH_IMMEDIATELY=True "
            "to demonstrate the cancel endpoint."
        )
        print()

    # Step 7: Poll the batch until it completes, fails, or is cancelled. Polling
    # makes long-running ingestion visible in the terminal.
    print("Step 7 - Polling batch status until it reaches a terminal state.")
    terminal_statuses = {"completed", "failed", "cancelled"}
    final_batch_state = None

    while True:
        batch = client.vector_stores.file_batches.retrieve(
            vector_store_id=vector_store_id,
            batch_id=batch_id,
        )
        print(
            "Batch status check:"
            f" status={batch.status},"
            f" counts={batch.file_counts}"
        )

        if batch.status in terminal_statuses:
            final_batch_state = batch
            break

        time.sleep(POLL_INTERVAL_SECONDS)

    print("Final batch state:")
    print(final_batch_state)
    print()

    # Step 8: List files that belong to this batch.
    print("Step 8 - Listing files that belong to this batch.")
    list_result = client.vector_stores.file_batches.list_files(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
        limit=20,
    )
    print("Files in batch:")
    print(list_result)
    print()

    # Step 9: Optional cleanup. These flags are False by default so beginners
    # can inspect the uploaded files after the first run.
    print("Step 9 - Running optional cleanup checks.")
    cleanup_uploaded_files(client=client, file_ids=uploaded_file_ids)
    cleanup_vector_store_files(
        client=client,
        vector_store_id=vector_store_id,
        file_ids=uploaded_file_ids,
    )

if __name__ == "__main__":
    main()
