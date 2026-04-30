"""What this file does:
Shows vector store file batch create/retrieve/list and optional cancel.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_batch.py
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

VECTOR_STORE_ID = ""  # Set here, or create env var VECTOR_STORE_ID.
FILE_IDS = [""]  # Put one or more file ids here. Example: ["file_abc", "file_def"].
BATCH_ATTRIBUTES = {"category": "sample"}
CANCEL_BATCH_AT_END = False

def _get_file_ids() -> list[str]:
    clean_ids = [file_id.strip() for file_id in FILE_IDS if file_id and file_id.strip()]
    if clean_ids:
        return clean_ids

    raw = os.getenv("VECTOR_FILE_IDS", "").strip()
    env_ids = [item.strip() for item in raw.split(",") if item.strip()]
    return env_ids

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve required batch inputs.
    vector_store_id = VECTOR_STORE_ID or os.getenv("VECTOR_STORE_ID", "").strip()
    if not vector_store_id:
        raise ValueError(
            "Missing vector store id. Set VECTOR_STORE_ID constant in this file "
            "or create env var VECTOR_STORE_ID."
        )

    file_ids = _get_file_ids()
    if not file_ids:
        raise ValueError(
            "Missing file ids. Set FILE_IDS constant in this file "
            "or create env var VECTOR_FILE_IDS (comma-separated)."
        )

    # Step 3: Create file batch.
    batch = client.vector_stores.file_batches.create(
        vector_store_id=vector_store_id,
        file_ids=file_ids,
        attributes=BATCH_ATTRIBUTES, #type: ignore
    )
    print(batch)
    batch_id = batch.id

    # Step 4: Retrieve file batch.
    retrieve_result = client.vector_stores.file_batches.retrieve(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
    )
    print(retrieve_result)

    # Step 5: List files in batch.
    list_result = client.vector_stores.file_batches.list_files(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
        limit=20,
    )
    print(list_result)

    # Step 6: Optional cancel.
    if CANCEL_BATCH_AT_END:
        cancel_result = client.vector_stores.file_batches.cancel(
            vector_store_id=vector_store_id,
            batch_id=batch_id,
        )
        print(cancel_result)
    else:
        print("Skipping cancel. Set CANCEL_BATCH_AT_END=True to cancel the created batch.")

if __name__ == "__main__":
    main()
