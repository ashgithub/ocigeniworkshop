"""Create a Shell-ready container with network policy and Skills.

The updated container docs show that `client.containers.create(...)` can include:
- `expires_after`
- `file_ids`
- `memory_limit`
- `network_policy`
- `skills`

This example connects the new container details to the Skills and Shell Tool
examples in this repo. It uses an inline local Skill by default so beginners can
see the full request shape while hosted Skill upload is still on hold.

By default this file runs in preview mode and does not call the API.

uv run openai_sdk/genai_client/containers/container_shell_skills.py
"""

from __future__ import annotations

import base64
import io
import os
import sys
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
RUN_LIVE_API = False

CONTAINER_NAME = "workshop-shell-skills-container"
CONTAINER_MEMORY_LIMIT = "4g"
CONTAINER_EXPIRES_AFTER_MINUTES = 5

# Use inline Skills while cloud hosted Skill upload is unavailable.
ATTACH_INLINE_SKILL = True
INLINE_SKILL_FOLDER = Path(__file__).resolve().parents[2] / "skills" / "samples" / "repo-tour-guide"

# Later, when cloud Skills are available, set ATTACH_INLINE_SKILL=False and
# replace this ID with a hosted or curated Skill ID.
HOSTED_OR_CURATED_SKILL_ID = "replace-with-skill-id"
HOSTED_OR_CURATED_SKILL_VERSION: str | int | None = "latest"

# Keep network disabled unless the workflow needs approved outbound domains.
ENABLE_NETWORK_ALLOWLIST = False
ALLOWED_NETWORK_DOMAINS = ["api.example.com"]

# Do not place real secrets in this file. Use a placeholder in preview mode and
# environment variables or a secret manager in real integrations.
ENABLE_DOMAIN_SECRET_EXAMPLE = False
DOMAIN_SECRET_DOMAIN = "api.example.com"
DOMAIN_SECRET_NAME = "API_TOKEN"
DOMAIN_SECRET_VALUE = "<secret-value>"

DELETE_CONTAINER_AT_END = True

def zip_skill_folder_as_base64(skill_folder: Path) -> str:
    archive_buffer = io.BytesIO()
    with ZipFile(archive_buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(skill_folder.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(skill_folder.parent).as_posix())

    return base64.b64encode(archive_buffer.getvalue()).decode("ascii")

def main() -> None:

    client: OpenAI = OpenAIClientProvider().oci_openai_client
    encoded_zip = zip_skill_folder_as_base64(INLINE_SKILL_FOLDER)

    # Step 1: Create a container with lifecycle, memory, network policy, and Skills.
    container = client.containers.create(
        name=CONTAINER_NAME,
        expires_after={"anchor":"last_active_at","minutes":CONTAINER_EXPIRES_AFTER_MINUTES},
        memory_limit=CONTAINER_MEMORY_LIMIT,
        network_policy= {"type": "disabled"},
        # Different usages of network_policy
        # network_policy= {
        #     "type": "allowlist",
        #     "allowed_domains": ALLOWED_NETWORK_DOMAINS,
        # },
        # network_policy= {
        #     "type": "allowlist",
        #     "allowed_domains": ALLOWED_NETWORK_DOMAINS,
        #     "domain_secrets": [
        #         {
        #             "domain":DOMAIN_SECRET_DOMAIN,
        #             "name":DOMAIN_SECRET_NAME,
        #             "value":DOMAIN_SECRET_VALUE
        #         }
        #     ]
        # },
        skills=[
            # {
            #     "type": "skill_reference",
            #     "skill_id":HOSTED_OR_CURATED_SKILL_ID, #type:ignore
            #     "version":HOSTED_OR_CURATED_SKILL_VERSION
            # },
            {
                "type": "inline",
                "name": INLINE_SKILL_FOLDER.name,
                "description": (
                    "Create developer handoff notes, adoption checklists, reviewer notes, "
                    "and risk summaries for sample-workshop changes."
                ),
                "source": {
                    "type": "base64",
                    "media_type": "application/zip",
                    "data": encoded_zip,
                },
            }
        ]
    )
    
    print(f"Created shell + skills container: {container.id}\n")

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
        input=(
            f"Use the `{INLINE_SKILL_FOLDER.name}` Skill. "
            "The Skill is mounted separately from container files, so do not "
            "look for the Skill bundle under /mnt/data. "
            "Create /mnt/data/explain_repo.md. "
            "The file should explain how container create options, Shell Tool, "
            "container files, and Skills work together. Print the final report."
        )
    )

    print("<------------- Shell + Skills response ------------>\n")
    print(response.output_text)

    # Step 3: List generated files for inspection or retrieval.
    files_page = client.containers.files.list(container_id=container.id, limit=20, order="desc")
    print("\n<------------- Container files ------------>")
    for container_file in files_page.data:
        print(
            f"id={container_file.id} | path={getattr(container_file, 'path', 'unknown')} | "
            f"bytes={getattr(container_file, 'bytes', 'unknown')}"
        )

    if DELETE_CONTAINER_AT_END:
        client.containers.delete(container.id)
        print(f"\nDeleted container: {container.id}")


if __name__ == "__main__":
    main()
