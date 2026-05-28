"""What this file does:
Demonstrates the simplest hosted skill usage flow with the Shell tool:
1) attach a hosted skill to `container_auto`
2) ask the model to use that skill
3) print the final text response

Documentation for reference:
- Skills guide in OCI GenAI agentic docs
- Containers API + Shell tool usage with `skills`

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm the selected model supports hosted shell in your environment.
- Replace `SKILL_ID` with a real hosted skill id before running.

How to run from repo root:
uv run openai_sdk/skills/skill_usage.py

Safe experiments:
1. Change the prompt to ask for a different output style.
2. Switch `version` from `latest` to an explicit number after uploading a new version.
3. Print the full response object to inspect tool output items.
"""

from __future__ import annotations

import os
import sys

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
PROMPT = (
    "Use the attached skill to explain what the skill does and create a short "
    "study note for a beginner."
)


def main() -> None:
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    #Step 2: check for skills
    skills_page = client.skills.list(limit=5, order="desc")
    sample_skill = skills_page.data[0]
    print("Using sample skill with:")
    print(f"Name: {sample_skill.name}\nVersion: {sample_skill.latest_version}\nDescription: {sample_skill.description}")

    # Step 2: Ask the model to use a hosted skill through the Shell tool.
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "skills": [
                        {
                            "type": "skill_reference",
                            "skill_id": sample_skill.id,
                            "version": sample_skill.latest_version,
                        }
                    ],
                },
            }
        ],
        input=PROMPT,
    )

    print("<------------- Hosted skill response ------------>\n")
    print(response.output_text)


if __name__ == "__main__":
    main()