---
name: module-docs-explainer
description: Mid-level guide for explaining modules in this repo using bundled reference notes plus repository README files. Use when a user asks to understand a module, compare OpenAI SDK, LangChain, OCI-native, database, RAG, agents, skills, or multimodal paths, or get examples and references without running scripts.
---

# Module Docs Explainer

Use this skill to turn repo docs into a clear learning explanation. It is mid-level: load a small reference file when useful, then inspect the actual README or module files before answering.

## Workflow

1. Read `references/module-map.md` when the user asks where a topic lives.
2. Read `references/explanation-examples.md` when the user asks for a learning path, comparison, or module explanation.
3. Inspect the relevant repo README before giving detailed guidance.
4. Explain the module in terms of purpose, best entry docs, runnable examples, prerequisites, and a small practice task.
5. Keep file recommendations focused; prefer 3-6 concrete paths over a directory dump.

## Output Shape

Return these sections when they fit the request:

- `What this module teaches`
- `Best files to open`
- `How to read it`
- `Safe commands to try`
- `Watch outs`

Do not invent cloud/API results. If a script needs OCI credentials, say what must be configured before running it.
