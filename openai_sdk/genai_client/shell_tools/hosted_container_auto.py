""" What this file does:
Demonstrates the simplest hosted Shell Tool request with `container_auto`.

Use `container_auto` when you want OCI to provision or reuse a hosted execution
container for the request. Your application does not execute commands and does
not send `shell_call_output`; the hosted shell environment runs the commands.

Beginner mental model:
- Your Python script sends a prompt and a Shell Tool definition.
- The model decides which safe inspection commands are useful.
- The hosted container runs those commands and returns a final text answer.

Key difference:
- `container_auto`: simplest hosted shape, no explicit container id needed.
- `container_reference`: use when you already created a container and need that
  exact workspace for files, memory, Skills, or persistence.
- `local`: the model requests commands and your app executes approved commands.

Documentation for reference:
- Shell Tool guide: https://developers.openai.com/api/docs/guides/tools-shell
- Responses API reference: https://platform.openai.com/docs/api-reference/responses

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm your project and compartment values are valid.
- Run this only from a sandbox or approved learning environment.

How to run from repo root:
uv run openai_sdk/genai_client/shell_tools/hosted_container_auto.py

Safe experiments:
1. Change `PROMPT` to inspect different runtime facts.
2. Keep the commands non-destructive.
3. Compare this request body with `hosted_container_reference.py`.

Important sections:
1. Constants: choose the model and beginner-safe prompt.
2. Step 1: Build a configured OpenAI client.
3. Step 2: Send the hosted Shell Tool request and print the answer.
"""

from __future__ import annotations

import os
import sys
from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"

# Prompt content stays close to the top so beginners can safely experiment with
# the task without touching the API call structure below.
PROMPT = """
Use the shell tool to inspect the hosted workspace.
Run non-destructive commands to show:
- the current directory
- the top-level files
- Python and Node.js versions if available

Summarize what you found in a short final answer.
"""

def main() -> None:
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client
    print("Step 1/2: OpenAI client configured for hosted shell.")

    # Step 2: Send the hosted shell request.
    print("Step 2/2: Sending hosted container_auto shell request...")
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type":"shell",
                "environment": {
                    "type":"container_auto"
                }
            }
        ],
        input=PROMPT
    )
    print("<------------- Hosted container_auto response ------------>\n")
    print(response.output_text)


if __name__ == "__main__":
    main()
