---
name: team-comms-brief
description: Draft Slack announcements, Outlook follow-up emails, rollout notes, and audience-specific communication plans for developer enablement, innovation workshops, sample code launches, and internal platform updates.
license: Apache-2.0
compatibility: Requires Python 3.11+ for scripts/build_message_plan.py. Does not send Slack or Outlook messages; it drafts reviewed copy only.
metadata:
  owner: innovation-enablement
  version: "1.0"
---

# Team Comms Brief Skill

Use this Skill when a developer needs to turn a technical change into clear
team communication for Slack, Outlook, or an internal enablement channel.

## Workflow

1. Identify the audience, decision context, and the action you want people to take.
2. Read `references/channel_guidelines.md` for channel-specific guidance.
3. Use `templates/slack_update.md` for Slack copy and `templates/outlook_email.md` for email copy.
4. If structured input is available, run `scripts/build_message_plan.py` to produce a first draft.
5. Check that the message includes impact, status, next steps, owners, and where to ask questions.
6. Do not invent production dates, links, or approvals. Mark unknown values as `TBD`.

## Script Usage

Run from the repository root:

```powershell
python openai_sdk/skills/samples/team-comms-brief/scripts/build_message_plan.py --input openai_sdk/skills/samples/team-comms-brief/examples/workshop_update.json
```

The script accepts JSON that follows `schemas/message_plan.schema.json`.

## Output

Return a compact communication package with:

- Slack announcement
- Outlook email
- owner/action checklist
- assumptions or missing details

Keep the tone practical, calm, and easy for another team to reuse.
