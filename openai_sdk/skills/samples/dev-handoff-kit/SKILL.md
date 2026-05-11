---
name: dev-handoff-kit
description: Create developer handoff notes, sample-code adoption checklists, reviewer guidance, risk summaries, and team-ready implementation briefs for internal tooling, API demos, workshop repos, and cross-team enablement.
license: Apache-2.0
compatibility: Requires Python 3.11+ for scripts/build_handoff.py. Designed for local shell or inline Skill examples.
metadata:
  owner: innovation-enablement
  version: "1.0"
---

# Dev Handoff Kit Skill

Use this Skill when a developer needs to share a change with another team in a
repeatable, reviewable, adoption-friendly format.

## Workflow

1. Identify what changed, why it matters, and who needs to act.
2. Read `references/handoff_checklist.md` before writing the final brief.
3. Use `templates/handoff_note.md` as the output shape.
4. If structured input is available, run `scripts/build_handoff.py`.
5. Include verification, known gaps, rollout steps, and where the receiver should ask questions.
6. Be explicit about what is sample-only, preview-only, or blocked by unreleased cloud access.

## Script Usage

Run from the repository root:

```powershell
python openai_sdk/skills/samples/dev-handoff-kit/scripts/build_handoff.py --input openai_sdk/skills/samples/dev-handoff-kit/examples/local_skills_handoff.json
```

The script accepts JSON that follows `schemas/handoff.schema.json`.

## Output

Return a Markdown handoff with:

- purpose
- change summary
- files to inspect
- setup and run steps
- verification
- risks and open questions
- suggested Slack or Outlook follow-up line
