"""Beginner-friendly hosted Skill upload script.

The OCI Generative AI Skills docs show upload with curl:

    POST <endpoint>/openai/v1/skills
    Content-Type: multipart/form-data
    files=@./basic_math.zip;type=application/zip

This Python version does the same multipart upload with httpx, while reusing
OpenAIClientProvider for the endpoint, project, compartment, and OCI auth setup.

How to use:
1. Edit the configuration values just below this docstring.
2. Run from the repo root:

       uv run openai_sdk/skills/upload_skill.py

3. Copy the returned skill id into `base_skill.py` or `skill_usage.py`.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

import httpx
from oci_genai_auth import OciUserPrincipalAuth

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


# -----------------------------
# Edit these lines before running
# -----------------------------

# Use "create" for your first upload.
# Use "version" when uploading a new zip for an existing hosted skill.
# Use "set_default" when you only want to change which version is the default.
UPLOAD_MODE = "create"

# The zip must contain one top-level folder, and that folder must contain SKILL.md.
SKILL_ZIP_PATH = Path(__file__).with_name("sample_skill.zip")

# Required for UPLOAD_MODE = "version" or "set_default".
EXISTING_SKILL_ID = "replace-with-your-skill-id"

# Required for UPLOAD_MODE = "set_default".
DEFAULT_VERSION = 1

# Leave empty to use OpenAIClientProvider().oci_openai_skills_endpoint.
# The May PDF lists Skills on the Green PPE FRA base until GA:
# "https://ppe.inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com/20231130/openai/v1"
# You can also set OCI_OPENAI_SKILLS_ENDPOINT in .env or add
# oci.skills_endpoint in sandbox.yaml.
SKILLS_BASE_URL_OVERRIDE = ""

# Your provider already uses OCI IAM request signing. Leave this as True unless
# your environment specifically gave you a bearer API key for the curl example.
USE_OCI_IAM_AUTH = True

REQUEST_TIMEOUT_SECONDS = 120.0


def main() -> None:
    print("<------------- Hosted Skill upload ------------>\n")

    # Step 1: Load the same OCI config, project, and compartment used elsewhere
    # in this workshop.
    provider = OpenAIClientProvider()
    skills_base_url = (SKILLS_BASE_URL_OVERRIDE or provider.oci_openai_skills_endpoint).rstrip("/")
    upload_mode = UPLOAD_MODE.strip().lower()

    headers = {
        "Accept": "application/json",
        "OpenAI-Project": provider.oci_openai_project,
        "opc-compartment-id": provider.oci_compartment_id,
    }

    auth = None
    if USE_OCI_IAM_AUTH:
        config_file = str(provider.scfg["oci"].get("configFile", "~/.oci/config"))
        auth = OciUserPrincipalAuth(
            config_file=os.path.expanduser(config_file),
            profile_name=provider.oci_openai_profile,
        )
        auth_message = f"OCI IAM request signing with profile '{provider.oci_openai_profile}'"
    else:
        headers["Authorization"] = f"Bearer {provider.oci_openai_api_key}"
        auth_message = "Bearer API key from sandbox.yaml"

    print(f"Endpoint base: {skills_base_url}")
    print(f"Auth mode: {auth_message}")
    print(f"Upload mode: {upload_mode}\n")

    # Step 2: Check the beginner-editable values before calling the API.
    if upload_mode not in {"create", "version", "set_default"}:
        raise ValueError('UPLOAD_MODE must be "create", "version", or "set_default".')

    if upload_mode in {"version", "set_default"} and EXISTING_SKILL_ID == "replace-with-your-skill-id":
        raise ValueError("Set EXISTING_SKILL_ID before using version or set_default mode.")

    if upload_mode in {"create", "version"}:
        zip_path = SKILL_ZIP_PATH.expanduser().resolve()
        if not zip_path.exists():
            raise FileNotFoundError(f"Skill zip was not found: {zip_path}")
        if not zip_path.is_file():
            raise ValueError(f"SKILL_ZIP_PATH must point to a zip file: {zip_path}")
        if zip_path.suffix.lower() != ".zip":
            raise ValueError(f"Skill bundle must be a .zip file: {zip_path}")

        with ZipFile(zip_path) as archive:
            file_names = [
                name
                for name in archive.namelist()
                if name.strip() and not name.endswith("/")
            ]
            top_level_folders = {
                PurePosixPath(name).parts[0]
                for name in file_names
                if PurePosixPath(name).parts
            }
            skill_manifests = [
                name
                for name in file_names
                if PurePosixPath(name).name.lower() == "skill.md"
            ]

        if len(top_level_folders) != 1:
            raise ValueError(
                "The zip must contain exactly one top-level folder. "
                f"Found: {sorted(top_level_folders)}"
            )
        if len(skill_manifests) != 1:
            raise ValueError(
                "The zip must contain exactly one SKILL.md or skill.md file. "
                f"Found: {skill_manifests}"
            )

        print(f"Zip file: {zip_path}")
        print(f"Top-level skill folder: {next(iter(top_level_folders))}")
        print(f"Manifest: {skill_manifests[0]}\n")

    # Step 3: Build the exact HTTP request described by the docs.
    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, auth=auth) as client:
        if upload_mode == "create":
            request_url = f"{skills_base_url}/skills"
            print("Calling: POST /skills with multipart form field 'files'")
            with zip_path.open("rb") as skill_file:
                response = client.post(
                    request_url,
                    headers=headers,
                    files={"files": (zip_path.name, skill_file, "application/zip")},
                )

        elif upload_mode == "version":
            request_url = f"{skills_base_url}/skills/{EXISTING_SKILL_ID}/versions"
            print("Calling: POST /skills/{skill_id}/versions with multipart form field 'files'")
            with zip_path.open("rb") as skill_file:
                response = client.post(
                    request_url,
                    headers=headers,
                    files={"files": (zip_path.name, skill_file, "application/zip")},
                )

        else:
            request_url = f"{skills_base_url}/skills/{EXISTING_SKILL_ID}"
            print("Calling: POST /skills/{skill_id} with JSON default_version")
            response = client.post(
                request_url,
                headers={**headers, "Content-Type": "application/json"},
                json={"default_version": int(DEFAULT_VERSION)},
            )

    # Step 4: Show the service result in a copy-paste friendly way.
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        print("\nSkill request failed.")
        print(f"Status: {response.status_code}")
        print("Response body:")
        print(response.text)
        if response.status_code == 404 and "Path doesn't map" in response.text:
            print(
                "\nThis usually means the request used the regular Responses endpoint. "
                "Use the Skills endpoint from OpenAIClientProvider().oci_openai_skills_endpoint "
                "or set SKILLS_BASE_URL_OVERRIDE / OCI_OPENAI_SKILLS_ENDPOINT."
            )
        raise

    try:
        result = response.json()
    except json.JSONDecodeError:
        print("\nSkill request succeeded, but the response was not JSON:")
        print(response.text)
        return

    print("\nSkill request succeeded:")
    print(json.dumps(result, indent=2))

    returned_skill_id = result.get("id") or result.get("skill_id")
    returned_version = result.get("latest_version") or result.get("version")

    if returned_skill_id:
        print(f"\nSkill id to reuse: {returned_skill_id}")
    if returned_version:
        print(f"Version returned: {returned_version}")

    print("\nNext step:")
    if upload_mode == "create":
        print("Paste the skill id into `skill_usage.py` as SKILL_ID.")
    elif upload_mode == "version":
        print("Use `version: latest` while testing, or set DEFAULT_VERSION to this version.")
    else:
        print("Create a new container or hosted shell environment to attach the new default version.")


if __name__ == "__main__":
    main()
