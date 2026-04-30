"""What this file does:
Demonstrates container file operations:
1) Upload a file into a container
2) List files in that container
3) Retrieve file metadata
4) Retrieve file content
5) Delete the file from the container

How to run:
uv run openai_sdk/genai_client/containers/container_files.py

Setup:
- Credentials are loaded from `sandbox.yaml` through `OpenAIClientProvider`.
- Replace placeholder values (`container_id`, `file_id`) with real ids.
- Ensure `data.csv` exists (or replace with your local test file path).

Notes for beginners:
- Start by running upload + list only, then add retrieve/content/delete.
- Keeping each operation explicit helps visualize the file workflow.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
BASIC_PROMPT = "When did the Roman Empire fall?"
STREAM_PROMPT = "Why the sky is blue?"

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # create container file
    container_file = client.containers.files.create(
        container_id="container_id",
        file=open("data.csv", "rb"),
    )
    print(container_file.id)

    # list container files
    page = client.containers.files.list(
        container_id="container_id",
    )
    page = page.data[0]
    print(page.id)

    # retrieve container files
    file = client.containers.files.retrieve(
        file_id="file_id",
        container_id="container_id",
    )
    print(file.id)

    # retrieve container file content
    content = client.containers.files.content.retrieve(
        file_id="file_id",
        container_id="container_id",
    )
    print(content)
    data = content.read()
    print(data)

    # delete container file
    client.containers.files.delete(
        file_id="file_id",
        container_id="container_id",
    )
