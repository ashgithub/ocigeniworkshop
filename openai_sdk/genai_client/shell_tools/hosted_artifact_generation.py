""" What this file does:
Demonstrates hosted Shell Tool artifact generation and retrieval.

Use this pattern when the shell should create files that your application can
list and retrieve later. A named `container_reference` keeps the generated
artifact in a known hosted workspace while the container is alive.

Beginner mental model:
- The model uses hosted shell commands to write a file under `/mnt/data`.
- Your Python app lists files from the hosted container through the API.
- Your app retrieves the generated file content and prints it locally.

Key difference:
- Plain hosted shell: good for command output and final text answers.
- Artifact workflow: create files under `/mnt/data`, then use container files.
- Container files: the application lists and retrieves generated outputs.

Documentation for reference:
- Shell Tool guide: https://developers.openai.com/api/docs/guides/tools-shell
- Containers API reference: https://platform.openai.com/docs/api-reference/containers
- Container files API reference: https://platform.openai.com/docs/api-reference/container-files

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm hosted Shell Tool and container files are enabled.
- Run this only from a sandbox or approved learning environment.

How to run from repo root:
uv run openai_sdk/genai_client/shell_tools/hosted_artifact_generation.py

Safe experiments:
1. Change `GENERATED_REPORT_PATH` to another `/mnt/data/*.md` file.
2. Keep generated artifacts small while learning.
3. Enable cleanup only after you have inspected the files you created.

Important sections:
1. Constants: name the hosted container and generated artifact path.
2. Helper functions: build the prompt, decode file content, and find files.
3. Step 1: Create a hosted container.
4. Step 2: Ask Shell Tool to write a report file.
5. Step 3: List container files.
6. Step 4: Retrieve the generated report content.
"""
import os
import sys
from typing import Any
from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"

# These constants define the hosted workspace and artifact name used in the
# example. Beginners can safely change the name or report path for experiments.
CONTAINER_NAME = "workshop-shell-artifact"
CONTAINER_MEMORY_LIMIT = "1g"
CONTAINER_EXPIRES_AFTER_MINUTES = 5

GENERATED_REPORT_PATH = "/mnt/data/shell_tool_report.md"
DELETE_CONTAINER_AT_END = True

def shell_prompt() -> str:
    """Build the instruction that tells hosted shell what file to create."""
    return f"""
Use the shell tool to create `{GENERATED_REPORT_PATH}`.

The Markdown report should include:
- runtime versions available in the hosted container
- files visible in the current workspace
- a short explanation of when Shell Tool artifact generation is useful

After writing the file, print its contents.
"""

def text_from_content_stream(content: Any) -> str:
    """Read container file content and return it as displayable text."""
    data = content.read()
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    return str(data)

def find_file_by_path(files: list[Any], path_suffix: str) -> Any | None:
    """Find the generated file object by matching the end of its path."""
    for container_file in files:
        file_path = getattr(container_file, "path", "")
        if file_path.endswith(path_suffix):
            return container_file
    return None

def main() -> None:
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 1: Create a named container so generated files can be inspected.
    print("Step 1/4: Creating hosted artifact container...")
    container = client.containers.create(
        name = CONTAINER_NAME,
        expires_after = {"anchor":"last_active_at","minutes":CONTAINER_EXPIRES_AFTER_MINUTES},
        memory_limit = CONTAINER_MEMORY_LIMIT,
        network_policy={"type":"disabled"}
    )
    print(f"Created artifact container: {container.id}\n")

    # Step 2: Ask Shell Tool to write a report inside the hosted container.
    print(f"Step 2/4: Asking hosted shell to create {GENERATED_REPORT_PATH}...")
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
        input=shell_prompt().strip()
    )
    print("<------------- Shell artifact response ------------>\n")
    print(response.output_text)

    # Step 3: List generated container files.
    print("Step 3/4: Listing files from the hosted container...")
    files_page = client.containers.files.list(container_id=container.id, limit=20, order="desc")
    print("\n<------------- Container files ------------>")
    for container_file in files_page.data:
        print(
            f"id={container_file.id} | path={getattr(container_file, 'path', 'unknown')} | "
            f"bytes={getattr(container_file, 'bytes', 'unknown')}"
        )

    # Step 4: Retrieve the generated report when it is present in the file list.
    print("Step 4/4: Looking for the generated report in the file list...")
    report_file = find_file_by_path(files_page.data, GENERATED_REPORT_PATH.rsplit("/", 1)[-1])
    if report_file:
        content = client.containers.files.content.retrieve(
            container_id=container.id,
            file_id=report_file.id,
        )
        print("\n<------------- Retrieved generated report ------------>\n")
        print(text_from_content_stream(content))
    else:
        print("\nGenerated report was not found in the latest container file list.")

    if DELETE_CONTAINER_AT_END:
        print("Cleanup: deleting the hosted artifact container...")
        client.containers.delete(container_id=container.id)
        print(f"\nDeleted container: {container.id}")


if __name__ == "__main__":
    main()
