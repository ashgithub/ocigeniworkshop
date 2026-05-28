# Skills Module (`openai_sdk/skills`)

This folder teaches the **most important beginner skills flows** in the OCI GenAI OpenAI-compatible API:

1. **Skills API basics**: list, retrieve, and inspect versions.
2. **Skill upload**: create a hosted skill and upload a new version from Python, once cloud Skills access is available.
3. **Local skills**: attach local Skill folders to a local shell request.
4. **Inline skills**: attach a base64-encoded zip Skill directly to a request.
5. **Curated skills**: attach provider-managed Skill references when they are available.
6. **Skill usage**: attach a hosted skill to the Shell tool and ask the model to use it.

For the shared explanation of how Skills connect to Shell Tool, containers, and tool execution, read:

- `openai_sdk/readme_shell_skills_containers.md`

## Suggested learning path

1. Start with `local_skill_usage.py`
   - Learn the local Skill request shape.
   - See the shell_call / shell_call_output loop needed for customer-managed local execution.

2. Run the bundled Skill scripts
   - Start with `samples/repo-tour-guide` for a minimal beginner skill.
   - Read `samples/module-docs-explainer` for a mid-level skill with references.
   - Run the local report script from `samples/workshop-result-runner`.

3. Run `inline_skill_usage.py`
   - Learn how to zip a local Skill folder into an inline base64 Skill reference.

4. Run `curated_skill_usage.py`
   - Learn how curated Skill IDs are attached as `skill_reference` entries.

5. Keep `upload_skill.py`, `base_skill.py`, and `skill_usage.py` for hosted Skills later
   - Upload, list, and attach hosted Skills after the cloud endpoint is released for your environment.

## Folder contents

1. `base_skill.py`
   - Skills API read operations.
   - Good first file for understanding skill objects and versions.

2. `upload_skill.py`
   - Beginner-friendly Skills API CRUD script with editable values at the top of the file.
   - Uses the same OCI user principal signing pattern as the other workshop examples.
   - Covers:
     - `GET /openai/v1/skills`
     - `GET /openai/v1/skills/{skill_id}`
     - `POST /openai/v1/skills`
     - `GET /openai/v1/skills/{skill_id}/versions`
     - `GET /openai/v1/skills/{skill_id}/versions/{version}`
     - `POST /openai/v1/skills/{skill_id}/versions`
     - `POST /openai/v1/skills/{skill_id}`
     - `DELETE /openai/v1/skills/{skill_id}`
     - `DELETE /openai/v1/skills/{skill_id}/versions/{version}`

3. `skill_usage.py`
   - Smallest hosted skill usage example in a Responses API call.
   - Uses the Shell tool with `container_auto`.

4. `local_skill_usage.py`
   - Local shell example using local Skill folders:
     - `samples/repo-tour-guide`
     - `samples/module-docs-explainer`
     - `samples/workshop-result-runner`
   - Requires a configured OCI OpenAI-compatible environment before live API calls.

5. `inline_skill_usage.py`
   - Builds a base64 zip from `samples/module-docs-explainer`.
   - Attaches it as an inline Skill.

6. `curated_skill_usage.py`
   - Shows provider-managed curated Skills such as `openai-spreadsheets`.
   - Run only after confirming the selected curated Skill is available for your model, provider, region, and release.

7. `samples/repo-tour-guide/`
   - Basic skill: a short repo tour with only `SKILL.md` plus UI metadata.
   - Use this as the smallest beginner-friendly local Skill example.

8. `samples/module-docs-explainer/`
   - Mid-level skill: explains repo modules using a compact `references/` folder.
   - Good for learning how progressive disclosure works without scripts.

9. `samples/workshop-result-runner/`
   - Scripted skill: scans the repo locally and produces a learning report.
   - Includes a small `scripts/` helper and a safety reference.

## Typical beginner workflow

1. Start by reading `local_skill_usage.py`.
2. Inspect the Skill folders under `samples/`.
3. Run the bundled local report script in `samples/workshop-result-runner`.
4. Read `inline_skill_usage.py` to see the base64 zip shape.
5. When hosted Skills are available, zip a Skill folder so the zip contains **one top-level folder**.
6. Open `upload_skill.py` and update `UPLOAD_MODE`, `SKILL_ZIP_PATH`, and optional skill/version values.
7. Copy the returned `skill_id`.
8. Paste that id into `base_skill.py` or `skill_usage.py`.

## Notes

- Skills guide the model, while Shell Tool and containers provide the execution environment.
- Skills can be attached to hosted containers, inline requests, or local shell workflows depending on the mode.
- Hosted skills are versioned bundles.
- If you see `Path doesn't map to a registered service`, check `OCI_OPENAI_SKILLS_ENDPOINT` or `oci.skills_endpoint`; the May PDF lists Skills on the `/20231130/openai/v1` early-access base.
- Local shell mode means your application executes commands and returns `shell_call_output`; OCI does not execute local commands for you.
- Inline Skills are useful for request-scoped demos because they do not require creating a hosted Skill resource.
- Curated Skills are provider-managed and their IDs can vary by model, provider, region, and release.
- `default_version` is used when a skill reference does not specify a version.
- `latest` is useful while learning, but explicit integer versions are better for stable demos.
- Keep beginner skills small: short `SKILL.md`, few files, one clear purpose.

## Run examples from repo root

- `uv run openai_sdk/skills/base_skill.py`
- `uv run openai_sdk/skills/local_skill_usage.py`
- `uv run openai_sdk/skills/inline_skill_usage.py`
- `uv run openai_sdk/skills/curated_skill_usage.py`
- `.venv\Scripts\python.exe openai_sdk/skills/samples/workshop-result-runner/scripts/repo_learning_report.py`
- `.venv\Scripts\python.exe openai_sdk/skills/samples/workshop-result-runner/scripts/repo_learning_report.py --topic skills`
- `uv run openai_sdk/skills/upload_skill.py`
- `uv run openai_sdk/skills/skill_usage.py`
