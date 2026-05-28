""" What this file does:
Demonstrates how to create a Shell-ready container with network policy and Skills:
1) Package a local Skill folder as a base64 zip
2) Create a hosted container with lifecycle, memory, network, and Skill settings
3) Use the Responses API Shell Tool with that existing container
4) List generated files in the container
5) Delete the container when cleanup is enabled

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Containers API reference: https://platform.openai.com/docs/api-reference/containers
- Responses API tools reference: https://platform.openai.com/docs/api-reference/responses/create
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm Shell Tool and Skills access are enabled for your project.
- Keep network disabled unless your workflow needs approved outbound domains.
- Do not put real secrets in this file; use placeholders for learning.

How to run from repo root:
uv run openai_sdk/genai_client/containers/container_shell_skills.py

Safe experiments:
1. Change the local Skill folder after reviewing `openai_sdk/skills/samples`.
2. Try one of the commented `network_policy` blocks after choosing approved domains.
3. Set `DELETE_CONTAINER_AT_END=False` while inspecting generated files.

Important sections:
1. Step 1: Build configured OpenAI client and package the inline Skill.
2. Step 2: Create the container with lifecycle, memory, network, and Skill settings.
3. Step 3: Run the Shell Tool in the created container.
4. Step 4: List generated files for inspection.
5. Step 5: Clean up the container when enabled.
"""

import base64
import io
import os
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from openai import OpenAI

# Allow this sample to import the shared client provider when run from repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"

# Container settings used by the create call below.
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

# Do not place real secrets in this file. Use a placeholder while learning and
# environment variables or a secret manager in real integrations.
ENABLE_DOMAIN_SECRET_EXAMPLE = False
DOMAIN_SECRET_DOMAIN = "api.example.com"
DOMAIN_SECRET_NAME = "API_TOKEN"
DOMAIN_SECRET_VALUE = "<secret-value>"

def zip_skill_folder_as_base64(skill_folder: Path) -> str:
    """Package a local Skill folder as a base64 zip for inline Skill upload."""
    archive_buffer = io.BytesIO()
    with ZipFile(archive_buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(skill_folder.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(skill_folder.parent).as_posix())

    return base64.b64encode(archive_buffer.getvalue()).decode("ascii")

def main() -> None:
    # Step 1: Build a configured OpenAI client and package the inline Skill.
    print("<------------- Step 1: Configure client and package Skill ------------>")
    client: OpenAI = OpenAIClientProvider().oci_openai_client
    encoded_zip = zip_skill_folder_as_base64(INLINE_SKILL_FOLDER)
    print(f"Packaged inline Skill folder: {INLINE_SKILL_FOLDER}")

    # Step 2: Create a container with lifecycle, memory, network policy, and Skills.
    print("\n<------------- Step 2: Create shell + skills container ------------>")
    container = client.containers.create(
        name=CONTAINER_NAME,
        expires_after={"anchor":"last_active_at","minutes":CONTAINER_EXPIRES_AFTER_MINUTES},
        memory_limit=CONTAINER_MEMORY_LIMIT,
        network_policy= {"type": "disabled"},
        # Alternative network_policy shapes for later experiments:
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

    # Step 3: Ask the Responses API to run Shell Tool inside the created container.
    print("<------------- Step 3: Run Shell Tool with inline Skill ------------>")
    response = client.responses.create(
        model=MODEL_ID,
        tools=[
            {
                # Race conditions
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

    # Step 4: List generated files for inspection or retrieval.
    print("\n<------------- Step 4: List generated container files ------------>")
    files_page = client.containers.files.list(container_id=container.id, limit=20, order="desc")
    print("\n<------------- Container files ------------>")
    for container_file in files_page.data:
        print(
            f"id={container_file.id} | path={getattr(container_file, 'path', 'unknown')} | "
            f"bytes={getattr(container_file, 'bytes', 'unknown')}"
        )

    # Step 5: Delete the test container when cleanup is enabled.
    print("\n<------------- Step 5: Cleanup ------------>")
    client.containers.delete(container.id)
    print(f"\nDeleted container: {container.id}")

if __name__ == "__main__":
    main()
