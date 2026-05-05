"""What this file does:
Demonstrates file operations inside a container:
1) Upload a file into a container
2) List container files
3) Retrieve file metadata
4) Retrieve file content
5) Delete a container file

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Container files API reference: https://platform.openai.com/docs/api-reference/container-files
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Replace placeholder values (`container_id`, `file_id`) with real ids.
- Make sure `data.csv` exists locally (or replace with your own file path).

How to run from repo root:
uv run openai_sdk/genai_client/containers/container_files.py

Safe experiments:
1. Use a small CSV first to inspect content retrieval easily.
2. Run upload + list only before enabling delete.
3. Print full response objects to learn response schema.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Execute upload/list/retrieve/content/delete flow.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Get a container ID from the base_example.py file on this same folder

    # Step 2a: Upload file to container.
    container_file = client.containers.files.create(
        container_id="cntr-ord-36sxfvex1p7vfui2osvpyob0coxa0x7kt616cbqopb2awu8q",
        file=open("./openai_sdk/output/fema_outage_flyer.pdf", "rb"),
    )
    print("Uploaded file with ID:")
    print(container_file.id)

    # Step 2b: List container files.
    page = client.containers.files.list(
        container_id="cntr-ord-36sxfvex1p7vfui2osvpyob0coxa0x7kt616cbqopb2awu8q",
    )
    page = page.data[0]
    print("File data found:")
    print(page.id)

    # Step 2c: Retrieve file metadata.
    file = client.containers.files.retrieve(
        file_id=container_file.id,
        container_id="cntr-ord-36sxfvex1p7vfui2osvpyob0coxa0x7kt616cbqopb2awu8q",
    )
    print("File data retrieved")
    print(file.id)

    # Step 2d: Retrieve file content stream.
    content = client.containers.files.content.retrieve(
        file_id=container_file.id,
        container_id="cntr-ord-36sxfvex1p7vfui2osvpyob0coxa0x7kt616cbqopb2awu8q",
    )
    print(content)
    data = content.read()
    print(data)

    # Step 2e: Delete file from container.
    client.containers.files.delete(
        file_id=container_file.id,
        container_id="cntr-ord-36sxfvex1p7vfui2osvpyob0coxa0x7kt616cbqopb2awu8q",
    )

if __name__ == "__main__":
    main()
