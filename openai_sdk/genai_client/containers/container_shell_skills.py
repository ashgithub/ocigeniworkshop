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
"""

from __future__ import annotations

import base64
import io
import json
import os
import sys
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider


# -----------------------------
# Edit these lines before running
# -----------------------------

MODEL_ID = "openai.gpt-5.2"
RUN_LIVE_API = False

CONTAINER_NAME = "workshop-shell-skills-container"
CONTAINER_MEMORY_LIMIT = "4g"
CONTAINER_EXPIRES_AFTER_MINUTES = 30

# Use inline Skills while cloud hosted Skill upload is unavailable.
ATTACH_INLINE_SKILL = True
INLINE_SKILL_FOLDER = Path(__file__).resolve().parents[2] / "skills" / "samples" / "dev-handoff-kit"

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

DELETE_CONTAINER_AT_END = False


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


def inline_skill(redact_data: bool = False) -> dict[str, Any]:
    encoded_zip = zip_skill_folder_as_base64(INLINE_SKILL_FOLDER)
    return {
        "type": "inline",
        "name": INLINE_SKILL_FOLDER.name,
        "description": (
            "Create developer handoff notes, adoption checklists, reviewer notes, "
            "and risk summaries for sample-workshop changes."
        ),
        "source": {
            "type": "base64",
            "media_type": "application/zip",
            "data": f"<base64 zip omitted, {len(encoded_zip)} chars>" if redact_data else encoded_zip,
        },
    }


def skill_reference() -> dict[str, Any]:
    if HOSTED_OR_CURATED_SKILL_ID == "replace-with-skill-id":
        raise ValueError("Set HOSTED_OR_CURATED_SKILL_ID before using hosted or curated Skill mode.")

    skill: dict[str, Any] = {
        "type": "skill_reference",
        "skill_id": HOSTED_OR_CURATED_SKILL_ID,
    }
    if HOSTED_OR_CURATED_SKILL_VERSION is not None:
        skill["version"] = HOSTED_OR_CURATED_SKILL_VERSION
    return skill


def skills(redact_inline_data: bool = False) -> list[dict[str, Any]]:
    if ATTACH_INLINE_SKILL:
        return [inline_skill(redact_data=redact_inline_data)]
    return [skill_reference()]


def network_policy(redact_secret: bool = False) -> dict[str, Any]:
    if not ENABLE_NETWORK_ALLOWLIST:
        return {"type": "disabled"}

    policy: dict[str, Any] = {
        "type": "allowlist",
        "allowed_domains": ALLOWED_NETWORK_DOMAINS,
    }
    if ENABLE_DOMAIN_SECRET_EXAMPLE:
        policy["domain_secrets"] = [
            {
                "domain": DOMAIN_SECRET_DOMAIN,
                "name": DOMAIN_SECRET_NAME,
                "value": "<redacted>" if redact_secret else DOMAIN_SECRET_VALUE,
            }
        ]
    return policy


def create_container_payload(redact_inline_data: bool = False) -> dict[str, Any]:
    return {
        "name": CONTAINER_NAME,
        "expires_after": {
            "anchor": "last_active_at",
            "minutes": CONTAINER_EXPIRES_AFTER_MINUTES,
        },
        "memory_limit": CONTAINER_MEMORY_LIMIT,
        "network_policy": network_policy(redact_secret=redact_inline_data),
        "skills": skills(redact_inline_data=redact_inline_data),
    }


def shell_request(container_id: str) -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "tools": [
            {
                "type": "shell",
                "environment": {
                    "type": "container_reference",
                    "container_id": container_id,
                },
            }
        ],
        "input": (
            "Use the attached Skill to create /mnt/data/container_skill_handoff.md. "
            "The handoff should explain how container create options, Shell Tool, "
            "container files, and Skills work together. Print the final handoff."
        ),
    }


def preview_payload() -> dict[str, Any]:
    return {
        "step_1_create_container": create_container_payload(redact_inline_data=True),
        "step_2_use_shell_with_container_reference": shell_request("<container-id-from-step-1>"),
        "step_3_list_generated_files": "client.containers.files.list(container_id='<container-id-from-step-1>')",
    }


def main() -> None:
    if not RUN_LIVE_API:
        print("<------------- Container Shell + Skills preview ------------>\n")
        print(json.dumps(preview_payload(), indent=2))
        print("\nSet RUN_LIVE_API=True after container Shell and Skills access is enabled.")
        return

    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 1: Create a container with lifecycle, memory, network policy, and Skills.
    container = client.containers.create(**create_container_payload())
    print(f"Created shell + skills container: {container.id}\n")

    # Step 2: Use Shell Tool with that exact container so the attached Skills are available.
    response = client.responses.create(**shell_request(container.id))
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
