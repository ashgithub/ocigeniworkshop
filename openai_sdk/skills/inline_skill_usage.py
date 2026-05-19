"""Use an inline Skill without creating a hosted Skill resource first.

Inline Skills package a local Skill folder as a base64-encoded zip and attach it
directly to one request. This is useful for temporary, generated, or workshop
skills when hosted Skill upload is not available yet.

Beginner flow:
1. Inspect INLINE_SKILL_FOLDER and the prompt before running.
2. Change INLINE_SKILL_FOLDER to another folder under openai_sdk/skills/samples.
3. Run this file only when hosted shell with inline Skills is enabled.

uv run openai_sdk/skills/inline_skill_usage.py
"""

import base64
import io
import os
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
INLINE_SKILL_FOLDER = Path(__file__).resolve().parent / "samples" / "module-docs-explainer"

PROMPT = """
Use the inline module-docs-explainer Skill.

Explain the `openai_sdk/skills` module for a beginner developer:
- what it teaches
- which files to open first
- how local, inline, curated, and hosted Skills differ
- what is safe to run before cloud Skills access is available
"""

def zip_skill_folder_as_base64(skill_folder: Path) -> str:
    archive_buffer = io.BytesIO()
    with ZipFile(archive_buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(skill_folder.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(skill_folder.parent).as_posix())

    return base64.b64encode(archive_buffer.getvalue()).decode("ascii")


def build_inline_skill(skill_folder: Path) -> dict[str, object]:
    encoded_zip = zip_skill_folder_as_base64(skill_folder)
    return {
        "type": "inline",
        "name": skill_folder.name,
        "description": (
            "Explain repo modules using bundled references and current README files "
            "for OpenAI SDK, LangChain, OCI-native, database, RAG, agents, and skills."
        ),
        "source": {
            "type": "base64",
            "media_type": "application/zip",
            "data": encoded_zip,
        },
    }

def main() -> None:
    inline_skill = build_inline_skill(INLINE_SKILL_FOLDER)

    client: OpenAI = OpenAIClientProvider().oci_openai_client
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                "type":"shell",
                "environment":{
                    "type": "container_auto",
                    "skills":[inline_skill] #type:ignore
                }
            }
        ],
        input=PROMPT,
    )

    print("<------------- Inline Skill response ------------>\n")
    print(response.output_text)


if __name__ == "__main__":
    main()
