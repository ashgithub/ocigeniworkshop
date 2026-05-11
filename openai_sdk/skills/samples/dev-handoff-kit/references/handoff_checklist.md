# Developer Handoff Checklist

## Required Sections

- Purpose: why the change exists.
- Audience: who should use or review it.
- Files: the smallest useful list of files to inspect.
- Setup: commands or configuration required before use.
- Verification: commands already run and what remains untested.
- Constraints: environment, release, auth, region, and access limitations.
- Support path: where questions should go.

## Quality Bar

- Beginner readers can run the preview path without cloud write access.
- Scripts fail with clear messages when input is missing or malformed.
- Copy uses stable terms from the repo and docs.
- Examples avoid real secrets, customer data, or private endpoints.
- Any live cloud action is opt-in and obvious.

## Useful Follow-up Prompts

- "Turn this handoff into a Slack update for developers."
- "Create an Outlook email asking reviewers to validate the example."
- "List what a team must change before adopting this in their repo."
