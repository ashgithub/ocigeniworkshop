""" What this file does:
Demonstrates how container files become inputs for a Shell Tool workflow:
1) Create a hosted container
2) Upload a local Markdown file into that container
3) Ask the Shell Tool to read the uploaded file and generate a report
4) List files produced in the container
5) Retrieve the generated report content

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Containers API reference: https://platform.openai.com/docs/api-reference/containers
- Container files API reference: https://platform.openai.com/docs/api-reference/container-files
- Responses API tools reference: https://platform.openai.com/docs/api-reference/responses/create
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm Shell Tool access is enabled for your project and compartment.
- Keep network disabled unless your workflow needs approved outbound domains.
- This script creates a test container and then uses ids returned by the API.

How to run from repo root:
uv run openai_sdk/genai_client/containers/files_shell_flow.py

Safe experiments:
1. Edit `sample_container_input.md` and rerun the script.
2. Change `GENERATED_REPORT_PATH` to learn where Shell Tool writes files.
3. Set cleanup flags to `False` while inspecting generated artifacts.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create a Shell-ready container.
3. Step 3: Upload the sample file.
4. Step 4: Run the Shell Tool against the uploaded file.
5. Step 5: List and retrieve generated files.
6. Step 6: Clean up the uploaded file and container.
"""

import os
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

# Allow this sample to import the shared client provider when run from repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"

CONTAINER_NAME = "workshop-container-files-shell"
CONTAINER_MEMORY_LIMIT = "1g"
CONTAINER_EXPIRES_AFTER_MINUTES = 5

SAMPLE_INPUT_PATH = Path(__file__).with_name("sample_container_input.md")
GENERATED_REPORT_PATH = "/mnt/data/container_file_shell_report.md"

def shell_prompt(uploaded_path: str) -> str:
    """Build the instruction sent to the Shell Tool inside the hosted container."""
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
def text_from_content_stream(content: Any) -> str:
    """Read a container file content stream and return displayable text."""
    data = content.read()
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    return str(data)


def find_file_by_path(files: list[Any], path_suffix: str) -> Any | None:
    """Find the first listed container file whose path ends with the target name."""
    for container_file in files:
        file_path = getattr(container_file, "path", "")
        if file_path.endswith(path_suffix):
            return container_file
    return None


def main() -> None:
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    print("<------------- Step 1: Configure OpenAI client ------------>")
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Create a hosted container that the Shell Tool can use as its workspace.
    print("\n<------------- Step 2: Create container ------------>")
    container = client.containers.create(
        name=CONTAINER_NAME,
        expires_after={"anchor":"last_active_at","minutes":5},
        memory_limit=CONTAINER_MEMORY_LIMIT,
        network_policy={"type":"disabled"}
    )
    print(f"Created container: {container.id}")

    # Step 3: Upload a local file into the container workspace.
    print("\n<------------- Step 3: Upload sample file ------------>")
    with SAMPLE_INPUT_PATH.open("rb") as file_handle:
        uploaded_file = client.containers.files.create(
            container_id=container.id,
            file=file_handle,
        )
    uploaded_path = getattr(uploaded_file, "path", SAMPLE_INPUT_PATH.name)
    print(f"Uploaded file: {uploaded_file.id} at {uploaded_path}")

    # Step 4: Use Shell Tool with `container_reference` to process the uploaded file.
    print("\n<------------- Step 4: Run Shell Tool ------------>")
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type": "shell",
                "environment": {
                    "type": "container_reference",
                    "container_id": container.id,
                },
            }
        ],
        input=shell_prompt(uploaded_path),
    )
    print("\n<------------- Shell response ------------>\n")
    print(response.output_text)

    # Step 5a: List files in the container so generated artifacts are visible.
    print("\n<------------- Step 5a: List container files ------------>")
    files_page = client.containers.files.list(container_id=container.id, limit=20, order="desc")
    print("\n<------------- Container files ------------>")
    for container_file in files_page.data:
        print(
            f"id={container_file.id} | path={getattr(container_file, 'path', 'unknown')} | "
            f"bytes={getattr(container_file, 'bytes', 'unknown')}"
        )

    # Step 5b: Retrieve generated report content if the Shell Tool created it.
    print("\n<------------- Step 5b: Retrieve generated report ------------>")
    report_file = find_file_by_path(files_page.data, "container_file_shell_report.md")
    if report_file:
        content = client.containers.files.content.retrieve(
            container_id=container.id,
            file_id=report_file.id,
        )
        print("\n<------------- Retrieved generated report ------------>\n")
        print(text_from_content_stream(content))
    else:
        print("\nGenerated report was not found in the latest container file list.")

    # Step 6: Clean up the uploaded file and container according to the flags above.
    print("\n<------------- Step 6: Cleanup ------------>")
    client.containers.files.delete(container_id=container.id, file_id=uploaded_file.id)
    print(f"Deleted uploaded file: {uploaded_file.id}")
    client.containers.delete(container.id)
    print(f"Deleted container: {container.id}")


if __name__ == "__main__":
    main()
