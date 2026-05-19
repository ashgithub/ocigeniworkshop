# Containers Module (`genai_client/containers`)

This module introduces **container resources** and **container file operations** using the OpenAI-compatible client configured through OCI.

For the shared explanation of how containers connect to Shell Tool, Skills, and tool execution, read:

- `openai_sdk/readme_shell_skills_containers.md`

Use this folder when you want to learn how to:

1. Create, list, retrieve, and delete containers.
2. Upload files into a container and inspect their metadata/content.
3. Use containers as stateful workspaces for the Shell Tool.
4. Attach network policies and Skills during container creation.
5. Retrieve generated artifacts through the Container Files API.

## Prerequisites

- Valid OCI/OpenAI-compatible setup in `sandbox.yaml`.
- Access to a project/compartment with permissions for container operations.
- If you run `container_files.py`, provide:
  - The included sample PDF at `openai_sdk/output/fema_outage_flyer.pdf`, or your own small file path.
  - Cleanup awareness: the script deletes its uploaded file and test container at the end.
- Shell examples call the live API when run. Keep cleanup flags enabled for throwaway runs, or set them to `False` only when you intentionally want to inspect generated artifacts afterward.

Run scripts from repo root:

- `uv run openai_sdk/genai_client/containers/base_example.py`
- `uv run openai_sdk/genai_client/containers/container_files.py`
- `uv run openai_sdk/genai_client/containers/files_shell_flow.py`
- `uv run openai_sdk/genai_client/containers/container_shell_skills.py`

## Folder Contents

1. `base_example.py`
   - Demonstrates the base container lifecycle:
     - `client.containers.create(...)`
     - `client.containers.list()`
     - `client.containers.retrieve(...)`
     - `client.containers.delete(...)`
   - Best first file for understanding container resources.
   - Starting comments explain the lifecycle, setup, run command, safe experiments, and each numbered step.

2. `container_files.py`
   - Demonstrates file lifecycle inside a container:
     - Create a short-lived test container.
     - Upload file to a container.
     - List container files.
     - Retrieve file metadata.
     - Retrieve file content stream.
     - Delete a file from the container.
   - Good follow-up once `base_example.py` is clear.
   - Uses `print_preview(...)` so beginners can inspect returned content without flooding the terminal.

3. `files_shell_flow.py`
   - Demonstrates the newer container + Shell Tool workflow:
     - Create a container.
     - Upload `sample_container_input.md`.
     - Use Shell Tool with `container_reference`.
     - Generate a Markdown report inside `/mnt/data`.
     - List files and retrieve generated content.
   - Prints each major step before the API call so the terminal output matches the code flow.

4. `container_shell_skills.py`
   - Demonstrates newer `containers.create(...)` fields:
     - `expires_after`
     - `memory_limit`
     - `network_policy`
     - `skills`
   - Uses an inline local Skill by default so beginners can see the full shape while hosted Skill upload is on hold.
   - Uses Shell Tool with `container_reference` after creating the container.
   - Includes commented network policy variants for disabled networking, allowlists, and domain secrets.

5. `sample_container_input.md`
   - Small text input used by `files_shell_flow.py`.

6. `containers.ipynb`
   - Notebook version of container examples for interactive learning and step-by-step experiments.

## Suggested Learning Path

1. Start with `base_example.py` and run each operation one by one.
2. Move to `container_files.py` to practice file upload and retrieval.
3. Run `files_shell_flow.py` to see how uploaded files become Shell Tool inputs.
4. Run `container_shell_skills.py` to see how network policy and Skills attach at container creation time.
5. Use `containers.ipynb` to iterate with your own IDs and sample files.

## New Container Fields From The May 2026 Guide

`client.containers.create(...)` can now describe more of the hosted workspace:

1. `name`
   - Human-readable container name.
2. `expires_after`
   - Expiration policy such as `{"anchor": "last_active_at", "minutes": 30}`.
3. `file_ids`
   - Existing Files API file IDs to copy into the container at creation time.
4. `memory_limit`
   - Supported examples include `1g`, `4g`, `16g`, and `64g`.
5. `network_policy`
   - Use `{"type": "disabled"}` for no outbound network.
   - Use `{"type": "allowlist", "allowed_domains": [...]}` for scoped outbound access.
   - Domain secrets can expose scoped environment variables for approved domains.
6. `skills`
   - Attach hosted or curated Skills with `{"type": "skill_reference", "skill_id": "...", "version": "latest"}`.
   - Attach inline Skills with `{"type": "inline", "name": "...", "description": "...", "source": {"type": "base64", "media_type": "application/zip", "data": "..."}}`.

Skills are attached when the container is created. To use a different set of Skills, create a new container.

## Typical Use Cases

1. Preparing a reusable workspace for code-interpreter style workflows.
2. Managing data files that should be attached to an execution environment.
3. Processing uploaded files with the Shell Tool.
4. Generating reports, logs, transformed datasets, or diagnostics inside `/mnt/data`.
5. Creating reusable Shell containers with Skills and scoped network policy.
6. Testing API behavior for create/retrieve/delete operations before production integration.

## Safety Notes

- Keep network access disabled unless the workflow truly needs approved outbound domains.
- Never put real secrets in prompts, sample files, Skill bundles, or committed code.
- Prefer domain-scoped secrets or OCI Resource Principal where supported.
- Treat generated shell artifacts as untrusted until reviewed.
- Keep cleanup flags disabled while learning, then delete test files and containers intentionally.

## References

- [OpenAI Containers API](https://platform.openai.com/docs/api-reference/containers)
- [OpenAI Container Files API](https://platform.openai.com/docs/api-reference/container-files)
