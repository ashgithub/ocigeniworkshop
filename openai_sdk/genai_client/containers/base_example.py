"""What this file does:
Demonstrates basic container lifecycle operations:
1) Create a container
2) List containers
3) Retrieve one container
4) Delete one container

How to run:
uv run openai_sdk/genai_client/containers/base_example.py

Setup:
- Credentials are loaded from `sandbox.yaml` through `OpenAIClientProvider`.
- Replace placeholder ids like `container_id` before running retrieve/delete.

Notes for beginners:
- This sample keeps operations separate so each API call is easy to follow.
- You can comment out delete while testing if you want to inspect created resources.
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

    # create container
    container = client.containers.create(
        name="name",
    )
    print(container.id)

    # list containers
    page = client.containers.list()
    page = page.data[0]
    print(page.id)

    # retrieve container
    container = client.containers.retrieve(
        "container_id",
    )
    print(container.id)

    # delete container
    client.containers.delete(
        "container_id",
    )
