"""What this file does:
Demonstrates the beginner-friendly Skills API lifecycle:
1) list hosted skills
2) retrieve one skill by id
3) list versions for that skill

Documentation for reference:
- OCI GenAI Skills API: `/openai/v1/skills`
- OCI GenAI Skill Versions API: `/openai/v1/skills/{skill_id}/versions`
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Confirm `project`, `compartment`, and `profile` are valid.
- Replace `SKILL_ID` with a real hosted skill id before running retrieve/version calls.

How to run from repo root:
uv run openai_sdk/skills/base_skill.py

Safe experiments:
1. Run only the list call first.
2. Print the full skill objects instead of just ids and names.
3. Change `LIST_LIMIT` to inspect pagination behavior.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: List hosted skills.
3. Step 3: Retrieve one skill and inspect its versions.
"""

from __future__ import annotations

import os
import sys

from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


LIST_LIMIT = 10
SKILL_ID = "replace-with-your-skill-id"


def print_skill_summary(client: OpenAI) -> None:
    """List hosted skills in the current OCI GenAI project."""
    skills_page = client.skills.list(limit=LIST_LIMIT, order="desc")

    print("<------------- Hosted skills in this project ------------>")
    if not skills_page.data:
        print("No hosted skills were found. Upload one first with `upload_skill.py`.\n")
        return

    for skill in skills_page.data:
        print(
            f"id={skill.id} | name={skill.name} | "
            f"default_version={skill.default_version} | latest_version={skill.latest_version}"
        )
    print()


def print_skill_details(client: OpenAI, skill_id: str) -> None:
    """Retrieve one hosted skill and list its versions."""
    if skill_id == "replace-with-your-skill-id":
        print("Skip retrieve example: replace `SKILL_ID` with a real hosted skill id first.\n")
        return

    skill = client.skills.retrieve(skill_id)
    print("<------------- Skill details ------------>")
    print(f"id: {skill.id}")
    print(f"name: {skill.name}")
    print(f"description: {skill.description}")
    print(f"default_version: {skill.default_version}")
    print(f"latest_version: {skill.latest_version}\n")

    versions_page = client.skills.versions.list(skill_id=skill_id, limit=LIST_LIMIT, order="desc")
    print("<------------- Skill versions ------------>")
    if not versions_page.data:
        print("No versions were returned for this skill.\n")
        return

    for version in versions_page.data:
        print(
            f"skill_id={version.skill_id} | version={version.version} | "
            f"name={version.name}"
        )
    print()


def main() -> None:
    # Step 1: Build a configured OpenAI client for Skills endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: List hosted skills for the current project.
    print_skill_summary(client)

    # Step 3: Retrieve one hosted skill and inspect its versions.
    print_skill_details(client, SKILL_ID)


if __name__ == "__main__":
    main()
