"""Vector store file-batch sample.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/vector_batch.py

Required environment variables:
- VECTOR_STORE_ID: target vector store id
- VECTOR_FILE_IDS: comma-separated file ids (at least 1)

Optional environment variables:
- VECTOR_BATCH_ATTRIBUTES_JSON: JSON object for batch attributes
- VECTOR_CANCEL_BATCH: set to true to cancel the created batch
"""

from __future__ import annotations

import json

try:
    from .vector_genai_client import as_bool, get_client, get_env, print_section, require_env
except ImportError:
    from vector_genai_client import as_bool, get_client, get_env, print_section, require_env


def _parse_file_ids(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_attributes(raw: str | None) -> dict[str, str | float | bool]:
    if not raw:
        return {"category": "sample"}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("VECTOR_BATCH_ATTRIBUTES_JSON must be a JSON object.")
    return parsed


def main() -> None:
    client = get_client()
    vector_store_id = require_env("VECTOR_STORE_ID")
    raw_file_ids = require_env("VECTOR_FILE_IDS")
    file_ids = _parse_file_ids(raw_file_ids)
    if not file_ids:
        raise ValueError("VECTOR_FILE_IDS must contain at least one file id.")

    attributes = _parse_attributes(get_env("VECTOR_BATCH_ATTRIBUTES_JSON"))

    print_section("Create File Batch")
    batch = client.vector_stores.file_batches.create(
        vector_store_id=vector_store_id,
        file_ids=file_ids,
        attributes=attributes,
    )
    print(batch)

    batch_id = batch.id

    print_section("Retrieve File Batch")
    retrieve_result = client.vector_stores.file_batches.retrieve(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
    )
    print(retrieve_result)

    print_section("List Files in Batch")
    list_result = client.vector_stores.file_batches.list_files(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
        limit=20,
    )
    print(list_result)

    if as_bool("VECTOR_CANCEL_BATCH", default=False):
        print_section("Cancel File Batch")
        cancel_result = client.vector_stores.file_batches.cancel(
            vector_store_id=vector_store_id,
            batch_id=batch_id,
        )
        print(cancel_result)
    else:
        print("Skipping cancel. Set VECTOR_CANCEL_BATCH=true to cancel the created batch.")


if __name__ == "__main__":
    main()
