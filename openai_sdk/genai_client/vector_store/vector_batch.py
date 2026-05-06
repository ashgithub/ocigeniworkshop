"""What this file does:
Shows vector store file batch operations:
1) Create file batch
2) Retrieve batch status
3) List files in batch
4) Optionally cancel batch

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Vector store file batches API reference: https://platform.openai.com/docs/api-reference/vector-stores-file-batches
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Set `VECTOR_STORE_ID` and one or more `FILE_IDS` (or env var `VECTOR_FILE_IDS`).

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_batch.py

Safe experiments:
1. Start with one file id, then test multi-file batches.
2. Inspect retrieve/list outputs before trying cancel.
3. Use attributes to tag batches for troubleshooting.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Resolve vector store and file ids.
3. Step 3-6: Create/retrieve/list/cancel batch flow.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

FILE_IDS = [""]  # Put one or more file ids here. Example: ["file_abc", "file_def"].
BATCH_ATTRIBUTES = {"category": "sample_py_code"}
CANCEL_BATCH_AT_END = False

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve required batch inputs.
    vector_store_id = OpenAIClientProvider().oci_openai_vector_store_id
    if not vector_store_id:
        raise ValueError(
            "Missing vector store id. Set VECTOR_STORE_ID constant in this file "
            "or create env var VECTOR_STORE_ID."
        )

    # Step 3: Create file batch.
    #TODO: change the files ids for actual files to upload
    batch = client.vector_stores.file_batches.create(
        vector_store_id=vector_store_id,
        file_ids=FILE_IDS,
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
