"""Container Files + Shell Tool workflow.

The updated container docs describe containers as stateful hosted workspaces for
Shell Tool and Code Interpreter workflows. Container files are how applications
upload source inputs and retrieve generated artifacts.

This beginner example demonstrates the full shape:
1. Create or reuse a hosted container.
2. Upload a local file into that container.
3. Ask the Shell Tool to read the uploaded file and generate a report.
4. List container files.
5. Retrieve generated file content.

By default this file runs in preview mode and does not call the API.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider


# -----------------------------
# Edit these lines before running
# -----------------------------

MODEL_ID = "openai.gpt-5.2"
RUN_LIVE_API = False

CREATE_NEW_CONTAINER = True
EXISTING_CONTAINER_ID = "replace-with-container-id"

CONTAINER_NAME = "workshop-container-files-shell"
CONTAINER_MEMORY_LIMIT = "1g"
CONTAINER_EXPIRES_AFTER_MINUTES = 30

SAMPLE_INPUT_PATH = Path(__file__).with_name("sample_container_input.md")
GENERATED_REPORT_PATH = "/mnt/data/container_file_shell_report.md"

DELETE_UPLOADED_FILE_AT_END = False
DELETE_CONTAINER_AT_END = False


def create_container_payload() -> dict[str, Any]:
    return {
        "name": CONTAINER_NAME,
        "expires_after": {
            "anchor": "last_active_at",
            "minutes": CONTAINER_EXPIRES_AFTER_MINUTES,
        },
        "memory_limit": CONTAINER_MEMORY_LIMIT,
        "network_policy": {"type": "disabled"},
    }


def shell_prompt(uploaded_path: str) -> str:
    return f"""
Use the shell tool in this existing container.

Steps:
1. Read the uploaded file at `{uploaded_path}`.
2. Create a Markdown report at `{GENERATED_REPORT_PATH}`.
3. The report should include:
   - what the uploaded file says
   - how container files, Shell Tool, and Skills fit together
   - safe next steps for beginner developers
4. Print the report contents after writing it.
"""


def preview_payload() -> dict[str, Any]:
    return {
        "step_1_create_container": create_container_payload()
        if CREATE_NEW_CONTAINER
        else {"reuse_container_id": EXISTING_CONTAINER_ID},
        "step_2_upload_file": {
            "client.containers.files.create": {
                "container_id": "<container-id>",
                "file": str(SAMPLE_INPUT_PATH),
            }
        },
        "step_3_shell_request": {
            "model": MODEL_ID,
            "tools": [
                {
                    "type": "shell",
                    "environment": {
                        "type": "container_reference",
                        "container_id": "<container-id>",
                    },
                }
            ],
            "input": shell_prompt("<uploaded-container-file-path>").strip(),
        },
        "step_4_list_files": "client.containers.files.list(container_id='<container-id>')",
        "step_5_retrieve_report": (
            "client.containers.files.content.retrieve("
            "container_id='<container-id>', file_id='<generated-report-file-id>')"
        ),
    }


def text_from_content_stream(content: Any) -> str:
    data = content.read()
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    return str(data)


def find_file_by_path(files: list[Any], path_suffix: str) -> Any | None:
    for container_file in files:
        file_path = getattr(container_file, "path", "")
        if file_path.endswith(path_suffix):
            return container_file
    return None


def main() -> None:
    if not RUN_LIVE_API:
        print("<------------- Container Files + Shell preview ------------>\n")
        print(json.dumps(preview_payload(), indent=2))
        print("\nSet RUN_LIVE_API=True after container Shell Tool access is enabled.")
        return

    if not SAMPLE_INPUT_PATH.exists():
        raise FileNotFoundError(f"Sample input file was not found: {SAMPLE_INPUT_PATH}")

    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 1: Create or reuse a hosted container.
    if CREATE_NEW_CONTAINER:
        container = client.containers.create(**create_container_payload())
        container_id = container.id
        print(f"Created container: {container_id}")
    else:
        if EXISTING_CONTAINER_ID == "replace-with-container-id":
            raise ValueError("Set EXISTING_CONTAINER_ID or enable CREATE_NEW_CONTAINER.")
        container_id = EXISTING_CONTAINER_ID
        container = client.containers.retrieve(container_id)
        print(f"Using existing container: {container.id}")

    # Step 2: Upload a local file into the container workspace.
    with SAMPLE_INPUT_PATH.open("rb") as file_handle:
        uploaded_file = client.containers.files.create(
            container_id=container_id,
            file=file_handle,
        )
    uploaded_path = getattr(uploaded_file, "path", SAMPLE_INPUT_PATH.name)
    print(f"Uploaded file: {uploaded_file.id} at {uploaded_path}")

    # Step 3: Use Shell Tool with container_reference to process the uploaded file.
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type": "shell",
                "environment": {
                    "type": "container_reference",
                    "container_id": container_id,
                },
            }
        ],
        input=shell_prompt(uploaded_path),
    )
    print("\n<------------- Shell response ------------>\n")
    print(response.output_text)

    # Step 4: List files in the container.
    files_page = client.containers.files.list(container_id=container_id, limit=20, order="desc")
    print("\n<------------- Container files ------------>")
    for container_file in files_page.data:
        print(
            f"id={container_file.id} | path={getattr(container_file, 'path', 'unknown')} | "
            f"bytes={getattr(container_file, 'bytes', 'unknown')}"
        )

    # Step 5: Retrieve generated report content if it exists.
    report_file = find_file_by_path(files_page.data, "container_file_shell_report.md")
    if report_file:
        content = client.containers.files.content.retrieve(
            container_id=container_id,
            file_id=report_file.id,
        )
        print("\n<------------- Retrieved generated report ------------>\n")
        print(text_from_content_stream(content))
    else:
        print("\nGenerated report was not found in the latest container file list.")

    if DELETE_UPLOADED_FILE_AT_END:
        client.containers.files.delete(container_id=container_id, file_id=uploaded_file.id)
        print(f"Deleted uploaded file: {uploaded_file.id}")

    if DELETE_CONTAINER_AT_END and CREATE_NEW_CONTAINER:
        client.containers.delete(container_id)
        print(f"Deleted container: {container_id}")


if __name__ == "__main__":
    main()
