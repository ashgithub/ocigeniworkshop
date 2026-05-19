""" What this file does:
Demonstrates file operations inside a container:
1) Create a short-lived container for the file example
2) Upload a file into a container
3) List container files
4) Retrieve file metadata
5) Retrieve file content
6) Delete a container file

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Container files API reference: https://platform.openai.com/docs/api-reference/container-files
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm `openai_sdk/output/fema_outage_flyer.pdf` exists, or replace the path.
- This script creates a test container and then uses ids returned by the API.

How to run from repo root:
uv run openai_sdk/genai_client/containers/container_files.py

Safe experiments:
1. Use a small text or CSV file first to inspect content retrieval easily.
2. Run upload + list only before enabling delete.
3. Print full response objects to learn response schema.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create a container for the uploaded file.
3. Step 3: Upload a local file.
4. Step 4: List files in the container.
5. Step 6: Retrieve file metadata.
6. Step 7: Retrieve file content.
7. Step 8: Delete the uploaded file and container.
"""

from openai import OpenAI
import os
import sys

# Allow this sample to import the shared client provider when run from repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

PREVIEW_LIMIT = 500

# Helper function to preview returned content without filling the terminal.
def print_preview(label, value, limit=PREVIEW_LIMIT) -> None:
    """Print a short preview for bytes, strings, or stream-like response values."""
    if isinstance(value, bytes):
        total = len(value)
        unit = "bytes"
        preview = repr(value[:limit])
    else:
        text = str(value)
        total = len(text)
        unit = "characters"
        preview = text[:limit]

    if len(preview) > limit:
        preview = f"{preview[:limit]}..."
    elif total > limit:
        preview = f"{preview}..."

    print(f"{label} preview ({min(total, limit)} of {total} {unit}):")
    print(preview)


def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    print("<------------- Step 1: Configure OpenAI client ------------>")
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Create a short-lived container as in `base_example.py`.
    print("\n<------------- Step 2: Create container ------------>")
    container = client.containers.create(
        name="workshop_container",
        expires_after={"anchor":"last_active_at","minutes":5}
    )
    print(f"Created container with name: {container.name} and ID:")
    print(container.id)

    # Step 3: Upload a local file to the container workspace.
    print("\n<------------- Step 3: Upload file ------------>")
    container_file = client.containers.files.create(
        container_id=container.id,
        file=open("./openai_sdk/output/fema_outage_flyer.pdf", "rb"),
    )
    print("Uploaded file with ID:")
    print(container_file.id)

    # Step 4: List files in the container and inspect the first returned record.
    print("\n<------------- Step 4: List container files ------------>")
    page = client.containers.files.list(
        container_id=container.id,
    )
    page = page.data[0]
    print("File data found:")
    print(page.id)

    # Step 6: Retrieve file metadata by file id. This returns metadata, not bytes.
    print("\n<------------- Step 6: Retrieve file metadata ------------>")
    file = client.containers.files.retrieve(
        file_id=container_file.id,
        container_id=container.id,
    )
    print("File data retrieved")
    print(file.id)

    # Step 7: Retrieve file content. The response is stream-like, so read it
    # before printing the downloaded bytes.
    print("\n<------------- Step 7: Retrieve file content ------------>")
    content = client.containers.files.content.retrieve(
        file_id=container_file.id,
        container_id=container.id,
    )
    print_preview("File content response", content)
    data = content.read()
    print_preview("File data", data)

    # Step 8: Delete the uploaded file and then delete the test container.
    print("\n<------------- Step 8: Clean up file and container ------------>")
    client.containers.files.delete(
        file_id=container_file.id,
        container_id=container.id,
    )
    print(f"Deleted file with ID: {container_file.id}")

    client.containers.delete(
        container_id=container.id,
    )
    print(f"Deleted container with ID: {container.id}")

if __name__ == "__main__":
    main()
