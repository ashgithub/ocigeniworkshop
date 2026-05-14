---
name: repo-tour-guide
description: Beginner repo navigation for the OCI AI Developer Learning Path. Use when a user asks where to start, how the current repo is organized, what module to open first, or wants a plain-language tour of docs, notebooks, scripts, and learning paths.
---

# Repo Tour Guide

Use this skill to give a first, friendly map of the repo. Keep the answer practical and point the user to a small number of next files.

## Workflow

1. Read the root `README.md` first if the user's goal is broad.
2. Identify the user's likely path: OpenAI SDK, LangChain, OCI-native, database, RAG, agents, multimodal, or skills.
3. Point to 3-5 files or folders maximum, with one sentence for why each matters.
4. Recommend one safe first action, such as opening a README or running `uv run AISandboxEnvCheck.py`.
5. Mention environment needs only when they affect the next step.

## Quick Map

- `openai_sdk/`: preferred path for OpenAI-compatible OCI examples.
- `langChain/`: framework path for LLM apps, RAG, agents, tools, and multimodal flows.
- `oci_genai/`: OCI-native examples kept for direct SDK and legacy workflows.
- `database/`: Oracle Database AI examples, including Select AI, NL2SQL, RAG, and semantic cache.
- `openai_sdk/skills/`: examples for local, inline, curated, and hosted skills.

## Output Shape

Return:

- `Start here`: the best entry point.
- `Why`: short context for the recommendation.
- `Open next`: a short file list.
- `First safe command`: include only when the command is local and beginner-friendly.
