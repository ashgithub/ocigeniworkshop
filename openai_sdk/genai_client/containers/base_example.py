""" What this file does:
Demonstrates the basic container lifecycle in a beginner-friendly sequence:
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
- This script creates a test container and then uses ids returned by the API.

How to run from repo root:
uv run openai_sdk/genai_client/containers/base_example.py

Safe experiments:
1. Change `name` in create call to test naming conventions.
2. Comment out delete while learning so the created resource can be inspected.
3. Print full objects (not only ids) to inspect payload shape.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create a short-lived container.
3. Step 3: List available containers.
4. Step 4: Retrieve a container by id.
5. Step 5: Delete a container by id.
"""

from openai import OpenAI
import os
import sys

# Allow this sample to import the shared client provider when run from repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    print("<------------- Step 1: Configure OpenAI client ------------>")
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Create a short-lived hosted container for this workshop run.
    print("\n<------------- Step 2: Create container ------------>")
    container = client.containers.create(
        name="workshop_container",
        expires_after={"anchor":"last_active_at","minutes":5}
    )
    print(f"Created container with name: {container.name} and ID:")
    print(container.id)

    # Step 3: List available containers. The list endpoint returns a page object,
    # and `page.data` contains the container records.
    print("\n<------------- Step 3: List containers ------------>")
    page = client.containers.list()
    print("Available containers:")
    for container in page.data:
        print(container.name)
        print(container.id)
        print(container.status)
        print("-----------------------")
        # Optional client clean up while experimenting with test containers.
        # client.containers.delete(
        #     container_id=container.id
        # )

    # Step 4: Retrieve a container by id to confirm the resource can be fetched.
    # The current sample uses the `container` variable from the list loop above.
    print("\n<------------- Step 4: Retrieve container ------------>")
    container = client.containers.retrieve(
        container_id=container.id,
    )
    print("Retrieved container with ID:")
    print(container.id)

    # Step 5: Delete the retrieved container so this learning run cleans up.
    print("\n<------------- Step 5: Delete container ------------>")
    client.containers.delete(
        container_id=container.id,
    )
    print(f"Deleted container with ID: {container.id}")

if __name__ == "__main__":
    main()
