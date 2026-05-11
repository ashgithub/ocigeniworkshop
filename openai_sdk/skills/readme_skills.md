# Skills Module (`openai_sdk/skills`)

This folder teaches the **most important beginner skills flows** in the OCI GenAI OpenAI-compatible API:

1. **Skills API basics**: list, retrieve, and inspect versions.
2. **Skill upload**: create a hosted skill and upload a new version from Python, once cloud Skills access is available.
3. **Local skills**: attach local Skill folders to a local shell request.
4. **Inline skills**: attach a base64-encoded zip Skill directly to a request.
5. **Curated skills**: attach provider-managed Skill references when they are available.
6. **Skill usage**: attach a hosted skill to the Shell tool and ask the model to use it.

## Suggested learning path

1. Start with `local_skill_usage.py`
   - Learn the local Skill request shape.
   - See the shell_call / shell_call_output loop needed for customer-managed local execution.

2. Run the bundled Skill scripts
   - Generate a Slack plus Outlook package from `samples/team-comms-brief`.
   - Generate a developer handoff from `samples/dev-handoff-kit`.

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
   - Beginner-friendly upload script with editable values at the top of the file.
   - Uses `OpenAIClientProvider().oci_openai_skills_endpoint` because Skills are not served from the regular Responses endpoint in the May PDF.
   - Covers:
     - `POST /openai/v1/skills`
     - `POST /openai/v1/skills/{skill_id}/versions`
     - `POST /openai/v1/skills/{skill_id}`

3. `skill_usage.py`
   - Smallest hosted skill usage example in a Responses API call.
   - Uses the Shell tool with `container_auto`.

4. `local_skill_usage.py`
   - Local shell example using local Skill folders:
     - `samples/team-comms-brief`
     - `samples/dev-handoff-kit`
   - Defaults to preview mode so beginners can inspect the request before live API calls.

5. `inline_skill_usage.py`
   - Builds a base64 zip from `samples/team-comms-brief`.
   - Attaches it as an inline Skill.

6. `curated_skill_usage.py`
   - Shows provider-managed curated Skills such as `openai-spreadsheets`.
   - Defaults to preview mode because curated Skill availability varies by model, provider, region, and release.

7. `samples/sample_skill/`
   - Minimal local skill bundle example.
   - Use this folder as the simplest content you would zip and upload.

8. `samples/team-comms-brief/`
   - Mid-level Skill for Slack and Outlook communication plans.
   - Includes `scripts`, `templates`, `schemas`, `references`, `examples`, and `agents`.

9. `samples/dev-handoff-kit/`
   - Mid-level Skill for developer handoff notes and adoption checklists.
   - Includes `scripts`, `templates`, `schemas`, `references`, `examples`, and `agents`.

## Typical beginner workflow

1. Start with `local_skill_usage.py` in preview mode.
2. Inspect the Skill folders under `samples/`.
3. Run each bundled script with its example JSON input.
4. Try `inline_skill_usage.py` in preview mode to see the base64 zip shape.
5. When hosted Skills are available, zip a Skill folder so the zip contains **one top-level folder**.
6. Open `upload_skill.py` and update `UPLOAD_MODE`, `SKILL_ZIP_PATH`, and optional skill/version values.
7. Copy the returned `skill_id`.
8. Paste that id into `base_skill.py` or `skill_usage.py`.

## Notes

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
- `python openai_sdk/skills/samples/team-comms-brief/scripts/build_message_plan.py --input openai_sdk/skills/samples/team-comms-brief/examples/workshop_update.json`
- `python openai_sdk/skills/samples/dev-handoff-kit/scripts/build_handoff.py --input openai_sdk/skills/samples/dev-handoff-kit/examples/local_skills_handoff.json`
- `uv run openai_sdk/skills/upload_skill.py`
- `uv run openai_sdk/skills/skill_usage.py`
