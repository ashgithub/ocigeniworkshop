"""Use an inline Skill without creating a hosted Skill resource first.

Inline Skills package a local Skill folder as a base64-encoded zip and attach it
directly to one request. This is useful for temporary, generated, or workshop
skills when hosted Skill upload is not available yet.

Beginner flow:
1. Keep RUN_LIVE_API=False and run this file to inspect the inline payload shape.
2. Change INLINE_SKILL_FOLDER to another folder under openai_sdk/skills/samples.
3. Set RUN_LIVE_API=True only when hosted shell with inline Skills is enabled.
"""

from __future__ import annotations

import base64
import io
import json
import os
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
RUN_LIVE_API = False
INLINE_SKILL_FOLDER = Path(__file__).resolve().parent / "samples" / "team-comms-brief"

PROMPT = """
Use the inline team-comms-brief Skill.

Create a Slack launch note and an Outlook email for an internal workshop update:
- We added local and inline Skills demos.
- Hosted Skill upload remains paused until cloud Skills access is available.
- Audience: beginner developers and solution engineers.
- Tone: practical, concise, and useful for sharing with other teams.
"""


def validate_skill_folder(skill_folder: Path) -> None:
    if not skill_folder.exists() or not skill_folder.is_dir():
        raise FileNotFoundError(f"Skill folder was not found: {skill_folder}")

    manifests = [
        path for path in skill_folder.iterdir()
        if path.is_file() and path.name.lower() == "skill.md"
    ]
    if len(manifests) != 1:
        raise ValueError(f"Expected exactly one SKILL.md file in {skill_folder}. Found {len(manifests)}.")


def zip_skill_folder_as_base64(skill_folder: Path) -> str:
    validate_skill_folder(skill_folder)

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
            "Draft Slack announcements and Outlook follow-up emails for "
            "developer enablement, launches, releases, and workshop updates."
        ),
        "source": {
            "type": "base64",
            "media_type": "application/zip",
            "data": encoded_zip,
        },
    }


def main() -> None:
    inline_skill = build_inline_skill(INLINE_SKILL_FOLDER)
    tools = [
        {
            "type": "shell",
            "environment": {
                "type": "container_auto",
                "skills": [inline_skill],
            },
        }
    ]

    if not RUN_LIVE_API:
        preview_skill = dict(inline_skill)
        preview_source = dict(preview_skill["source"])  # type: ignore[arg-type]
        preview_source["data"] = f"<base64 zip omitted, {len(inline_skill['source']['data'])} chars>"  # type: ignore[index]
        preview_skill["source"] = preview_source
        print("<------------- Inline Skill request preview ------------>\n")
        print(json.dumps({"model": MODEL_ID, "tools": [{"type": "shell", "environment": {"type": "container_auto", "skills": [preview_skill]}}], "input": PROMPT.strip()}, indent=2))
        print("\nSet RUN_LIVE_API=True when inline hosted shell Skills are available.")
        return

    client: OpenAI = OpenAIClientProvider().oci_openai_client
    response = client.responses.create(
        model=MODEL_ID,
        tools=tools,
        input=PROMPT,
    )

    print("<------------- Inline Skill response ------------>\n")
    print(response.output_text)


if __name__ == "__main__":
    main()
