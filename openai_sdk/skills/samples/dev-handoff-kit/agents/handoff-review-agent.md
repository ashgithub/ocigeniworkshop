# Handoff Review Agent Notes

Use these notes when another agent reviews a developer handoff before it is
shared with a team.

## Review Checklist

- The purpose and target audience are clear.
- The files list is short enough for a reviewer to inspect.
- Run steps start with preview or dry-run behavior.
- Verification separates completed checks from untested live paths.
- Risks mention auth, release, region, and local execution constraints where relevant.
- Follow-up copy is short enough to paste into Slack or Outlook.

## Suggested Review Prompt

Review this handoff for beginner usability and adoption risk.
Return:

1. missing context
2. risky or unclear steps
3. a final Slack-ready summary
