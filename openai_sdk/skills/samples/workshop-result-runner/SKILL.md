---
name: workshop-result-runner
description: Scripted skill for collecting safe local learning results from this workshop repo. Use when a user asks to run a repo scan, summarize runnable examples, inspect learning modules, produce a Markdown learning report, or verify sample skill/module paths before deeper cloud or API runs.
---

# Workshop Result Runner

Use this skill when the user wants a simple, repeatable result from the repo instead of only a verbal tour. The bundled script scans local files and produces a compact learning report without calling cloud services.

## Workflow

1. Read `references/safe-run-guide.md` before running commands.
2. Run `scripts/repo_learning_report.py` from the repo root for a local inventory report.
3. Add `--topic <word>` when the user asks about a specific topic such as `rag`, `skills`, `agents`, `database`, or `openai_sdk`.
4. Return the script result plus a short interpretation.
5. If the user asks to run live AI or database demos, first identify required credentials, config, and expected side effects.

## Commands

Run a full local report:

```powershell
.venv\Scripts\python.exe openai_sdk/skills/samples/workshop-result-runner/scripts/repo_learning_report.py
```

Run a focused report:

```powershell
.venv\Scripts\python.exe openai_sdk/skills/samples/workshop-result-runner/scripts/repo_learning_report.py --topic rag
```

Return JSON for automation:

```powershell
.venv\Scripts\python.exe openai_sdk/skills/samples/workshop-result-runner/scripts/repo_learning_report.py --format json
```

## Output

Summarize:

- what was scanned
- the strongest starting point
- the local environment check
- example commands that may require sandbox or OCI setup
- credentials or sandbox setup needed before deeper runs
