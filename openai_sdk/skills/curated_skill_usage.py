"""Use provider-managed curated Skills.

Curated Skills are provider-managed Skill bundles. The May guide lists examples
such as `openai-spreadsheets`, `anthropic-xlsx`, `anthropic-docx`,
`anthropic-pdf`, and `anthropic-pptx`, while warning that availability can vary
by provider, model, region, and release.

This file does not upload anything. It shows how a curated Skill is attached as
a skill_reference, just like a hosted Skill ID.

uv run openai_sdk/skills/curated_skill_usage.py
"""
import os
import sys

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"


# Pick a curated Skill ID supported in your model/region. The PDF examples:
# - openai-spreadsheets
# - anthropic-xlsx
# - anthropic-docx
# - anthropic-pdf
# - anthropic-pptx
# CURATED_SKILL_ID = "openai-spreadsheets"
CURATED_SKILL_ID = "openai-docs"
# CURATED_SKILL_ID = "anthropic-pdf"
CURATED_SKILL_VERSION: str | int | None = "latest"

PROMPT = """
Use the curated spreadsheet Skill to inspect the attached workshop planning file.
Return a concise summary of:
1. open risks
2. owners
3. next actions for Slack and Outlook follow-up

For now this is a request-shape example. Add uploaded file IDs or container files
when curated Skills are enabled in your environment.
"""

def main() -> None:
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type":"shell",
                "environment":{
                    "type":"container_auto",
                    "skills":[
                        {
                            "type": "skill_reference",
                            "skill_id": CURATED_SKILL_ID,
                            "version": CURATED_SKILL_VERSION #type:ignore
                        }
                    ]
                }
            }
        ],
        input=PROMPT,
    )

    print("<------------- Curated Skill response ------------>\n")
    print(response.output_text)


if __name__ == "__main__":
    main()
