"""What this file does:
Demonstrates the container lifecycle in a beginner-friendly sequence:
1) Create a container
2) List containers
3) Retrieve one container by id
4) Delete one container by id

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Containers API reference: https://platform.openai.com/docs/api-reference/containers
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm `projectId`, `compartmentId`, and profile values are valid.
- Replace placeholder ids (`container_id`) with real ids before running retrieve/delete.

How to run from repo root:
uv run openai_sdk/genai_client/containers/base_example.py

Safe experiments:
1. Change `name` in create call to test naming conventions.
2. Comment out delete while learning so the created resource can be inspected.
3. Print full objects (not only ids) to inspect payload shape.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Run create/list/retrieve/delete container calls.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2a: Create container.
    container = client.containers.create(
        name="workshop_container",
        # expires_after=
    )
    print(f"Created container with name: {container.name} and ID:")
    print(container.id)

    # Step 2b: List available containers.
    page = client.containers.list()
    print(f"Available containers:")
    for container in page.data:
        print(container.name)
        print(container.id)

    # Step 2c: Retrieve container by id.
    container = client.containers.retrieve(
        container_id=container.id,
    )
    print(f"Retrieved container with ID:")
    print(container.id)

    # Step 2d: Delete container by id.
    client.containers.delete(
        container_id=container.id,
    )
    print(f"Deleted container with ID: {container.id}")

if __name__ == "__main__":
    main()
