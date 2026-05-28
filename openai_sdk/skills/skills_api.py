"""
Beginner-friendly Skills API CRUD example.

How to use:
1. Edit ACTION and the values below.
2. Run from the repo root:

       uv run openai_sdk/skills/skills_api.py

Actions:
- "list": show hosted skills in the project.
- "retrieve": show one hosted skill.
- "create": upload a new hosted skill zip.
- "version": upload a new version for an existing hosted skill.
- "list_versions": show versions for an existing hosted skill.
- "retrieve_version": show one version for an existing hosted skill.
- "set_default": change the default version for an existing hosted skill.
- "delete": delete one hosted skill.
- "delete_version": delete one version for an existing hosted skill.
"""

import json
import os
import sys
import uuid
from pathlib import Path

import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


# -----------------------------
# Edit these lines before running
# -----------------------------
ACTION = "create"
SKILL_ZIP_PATH = Path(__file__).with_name("repo-tour-guide.zip")
SKILL_ID = "replace-with-your-skill-id"
SKILL_VERSION = "1"
LIST_LIMIT = 5
REQUEST_TIMEOUT_SECONDS = 120


def main() -> None:
    provider = OpenAIClientProvider()
    base_url = provider.oci_openai_endpoint.rstrip("/")
    request_id = f"skill-{ACTION}-{uuid.uuid4()}"

    headers = {
        "Accept": "application/json",
        "OpenAI-Project": provider.oci_openai_project,
        "opc-compartment-id": provider.oci_compartment_id,
        "compartment-id": provider.oci_compartment_id,
        "opc-request-id": request_id,
    }

    auth = provider.get_raw_user_auth()

    print("<------------- Skills API example ------------>\n")
    print(f"Endpoint: {base_url}")
    print(f"Action: {ACTION}")
    print(f"opc-request-id: {request_id}\n")

    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, auth=auth) as client:
        if ACTION == "list":
            response = client.get(
                f"{base_url}/skills",
                headers=headers,
                params={"limit": LIST_LIMIT, "order": "desc"},
            )

        elif ACTION == "retrieve":
            response = client.get(f"{base_url}/skills/{SKILL_ID}", headers=headers)

        elif ACTION == "create":
            zip_path = SKILL_ZIP_PATH.expanduser().resolve()
            print(f"Zip path: {zip_path}\n")
            with zip_path.open("rb") as skill_zip:
                response = client.post(
                    f"{base_url}/skills",
                    headers=headers,
                    files={"files": (zip_path.name, skill_zip, "application/zip")},
                )

        elif ACTION == "version":
            zip_path = SKILL_ZIP_PATH.expanduser().resolve()
            print(f"Skill id: {SKILL_ID}")
            print(f"Zip path: {zip_path}\n")
            with zip_path.open("rb") as skill_zip:
                response = client.post(
                    f"{base_url}/skills/{SKILL_ID}/versions",
                    headers=headers,
                    files={"files": (zip_path.name, skill_zip, "application/zip")},
                )

        elif ACTION == "set_default":
            print(f"Skill id: {SKILL_ID}")
            print(f"Default version: {SKILL_VERSION}\n")
            response = client.post(
                f"{base_url}/skills/{SKILL_ID}",
                headers={**headers, "Content-Type": "application/json"},
                json={"default_version": SKILL_VERSION},
            )

        elif ACTION == "list_versions":
            response = client.get(
                f"{base_url}/skills/{SKILL_ID}/versions",
                headers=headers,
                params={"limit": LIST_LIMIT, "order": "desc"},
            )

        elif ACTION == "retrieve_version":
            response = client.get(
                f"{base_url}/skills/{SKILL_ID}/versions/{SKILL_VERSION}",
                headers=headers,
            )

        elif ACTION == "delete":
            print(f"Skill id: {SKILL_ID}\n")
            response = client.delete(f"{base_url}/skills/{SKILL_ID}", headers=headers)

        elif ACTION == "delete_version":
            print(f"Skill id: {SKILL_ID}")
            print(f"Version: {SKILL_VERSION}\n")
            response = client.delete(
                f"{base_url}/skills/{SKILL_ID}/versions/{SKILL_VERSION}",
                headers=headers,
            )

        else:
            raise ValueError(
                'ACTION must be "list", "retrieve", "create", "version", "list_versions", '
                '"retrieve_version", "set_default", "delete", or "delete_version".'
            )

    print(f"Status: {response.status_code}")
    print(f"Returned opc-request-id: {response.headers.get('opc-request-id', '<not returned>')}\n")

    if response.text:
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(response.text)

    response.raise_for_status()


if __name__ == "__main__":
    main()
