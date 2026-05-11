"""Use provider-managed curated Skills.

Curated Skills are provider-managed Skill bundles. The May guide lists examples
such as `openai-spreadsheets`, `anthropic-xlsx`, `anthropic-docx`,
`anthropic-pdf`, and `anthropic-pptx`, while warning that availability can vary
by provider, model, region, and release.

This file does not upload anything. It shows how a curated Skill is attached as
a skill_reference, just like a hosted Skill ID.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
RUN_LIVE_API = False

# Pick a curated Skill ID supported in your model/region. The PDF examples:
# - openai-spreadsheets
# - anthropic-xlsx
# - anthropic-docx
# - anthropic-pdf
# - anthropic-pptx
CURATED_SKILL_ID = "openai-spreadsheets"
CURATED_SKILL_VERSION: str | int | None = None

PROMPT = """
Use the curated spreadsheet Skill to inspect the attached workshop planning file.
Return a concise summary of:
1. open risks
2. owners
3. next actions for Slack and Outlook follow-up

For now this is a request-shape example. Add uploaded file IDs or container files
when curated Skills are enabled in your environment.
"""


def build_curated_skill_reference() -> dict[str, Any]:
    skill_reference: dict[str, Any] = {
        "type": "skill_reference",
        "skill_id": CURATED_SKILL_ID,
    }
    if CURATED_SKILL_VERSION is not None:
        skill_reference["version"] = CURATED_SKILL_VERSION
    return skill_reference


def build_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "shell",
            "environment": {
                "type": "container_auto",
                "skills": [build_curated_skill_reference()],
            },
        }
    ]


def main() -> None:
    tools = build_tools()

    if not RUN_LIVE_API:
        print("<------------- Curated Skill request preview ------------>\n")
        print(json.dumps({"model": MODEL_ID, "tools": tools, "input": PROMPT.strip()}, indent=2))
        print("\nSet CURATED_SKILL_ID to a supported Skill ID and RUN_LIVE_API=True when available.")
        return

    client: OpenAI = OpenAIClientProvider().oci_openai_client
    response = client.responses.create(
        model=MODEL_ID,
        tools=tools,
        input=PROMPT,
    )

    print("<------------- Curated Skill response ------------>\n")
    print(response.output_text)


if __name__ == "__main__":
    main()
