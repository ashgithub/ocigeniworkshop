""" What this file does:
Demonstrates hosted Shell Tool usage with an explicit `container_reference`.

Use `container_reference` when your app needs control over the hosted workspace:
container name, memory limit, expiration, uploaded files, network policy, or
attached Skills. The shell request points to the `container_id` you created or
reused.

Beginner mental model:
- First, your app creates a hosted container and receives its `container.id`.
- Next, the Responses API request passes that id in the Shell Tool environment.
- The model runs shell commands inside that exact hosted workspace.

Key difference:
- `container_auto`: quickest hosted shell request; no prior container step.
- `container_reference`: two-step hosted flow with a known container id.
- `local`: customer-managed execution with a `shell_call_output` loop.

Documentation for reference:
- Shell Tool guide: https://developers.openai.com/api/docs/guides/tools-shell
- Containers API reference: https://platform.openai.com/docs/api-reference/containers
- Responses API reference: https://platform.openai.com/docs/api-reference/responses

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm container operations are available in your tenancy.
- Run this only from a sandbox or approved learning environment.

How to run from repo root:
uv run openai_sdk/genai_client/shell_tools/hosted_container_reference.py

Safe experiments:
1. Change `CONTAINER_NAME` to make test containers easy to identify.
2. Change `CONTAINER_MEMORY_LIMIT` only to supported values in your environment.
3. Set `DELETE_CONTAINER_AT_END=False` when you want to inspect the container.

Important sections:
1. Constants: name the hosted container and lifecycle settings.
2. Step 1: Create a hosted container.
3. Step 2: Use Shell Tool with that exact container id.
4. Step 3: Optionally delete the test container.
"""

import os
import sys
from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"

# These constants define the hosted workspace before the model runs any shell
# commands. They are safe places for beginners to inspect the container shape.
CONTAINER_NAME = "workshop-shell-reference"
CONTAINER_MEMORY_LIMIT = "1g"
CONTAINER_EXPIRES_AFTER_MINUTES = 5

DELETE_CONTAINER_AT_END = True

# The prompt asks the hosted shell to inspect its own container workspace.
PROMPT = """
Use the shell tool in this explicit hosted container.
List the current directory, show disk usage if available, print runtime versions,
and summarize why an explicit container is useful.
"""

def main() -> None:
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 1: Create a hosted container with explicit lifecycle settings.
    print("Step 1/3: Creating hosted shell container...")
    container = client.containers.create(
        name=CONTAINER_NAME,
        expires_after={"anchor":"last_active_at","minutes":CONTAINER_EXPIRES_AFTER_MINUTES},
        memory_limit=CONTAINER_MEMORY_LIMIT,
        network_policy={"type":"disabled"}
    )
    print(f"Created shell container: {container.id}\n")

    # Step 2: Use Shell Tool with this exact container.
    print("Step 2/3: Sending shell request to the explicit container...")
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
        input=PROMPT
    )
    print("<------------- Hosted container_reference response ------------>\n")
    print(response.output_text)

    # Step 3: Delete the container only when the learner opted in.
    if DELETE_CONTAINER_AT_END:
        print("Step 3/3: Deleting the demo container...")
        client.containers.delete(container_id=container.id)
        print(f"\nDeleted container: {container.id}")
    else:
        print("Step 3/3: Container deletion skipped by DELETE_CONTAINER_AT_END.")


if __name__ == "__main__":
    main()
