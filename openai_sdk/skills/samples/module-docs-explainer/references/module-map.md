# Module Map

Use this reference as a lightweight orientation aid. Confirm details in the current repo files before answering.

## Primary Paths

| Path | Use it for | Good entry files |
|---|---|---|
| `README.md` | Full repo orientation, setup, learning paths | `README.md` |
| `openai_sdk/` | Recommended OpenAI-compatible OCI patterns | `readme_openai_sdk.md`, `genai_client/readme_genai.md`, `agent_sdk/readme_agent_sdk.md`, `skills/readme_skills.md` |
| `langChain/` | Framework-based chains, tools, RAG, agents, multimodal examples | `llm/readme_langchain_llm.md`, `agents/readme_agents.md`, `rag/readme_lang_rag.md` |
| `oci_genai/` | OCI-native examples and legacy/direct SDK flows | module READMEs under `llm/`, `function_calling/`, `rag/`, `speech/`, `vision/` |
| `database/` | Oracle Database AI examples | `readme_database.md`, `selectai_demo.py`, `nl2sql_demo.py` |

## Topic Hints

- Start with `openai_sdk/` for project-scoped Responses API examples, containers, memory, vector stores, skills, and Agents SDK.
- Start with `langChain/` for orchestration patterns and ecosystem integrations.
- Start with `database/` for Select AI, NL2SQL, semantic cache, and database-backed RAG.
- Start with `oci_genai/` only when the user specifically needs OCI-native lower-level examples.
- Start with `openai_sdk/skills/` when the user wants local, inline, curated, or hosted skill examples.

## Environment Notes

- Prefer `uv run <path/to/script.py>` from the repo root.
- Use `uv run AISandboxEnvCheck.py` as the first environment check.
- Many AI and database examples require `sandbox.yaml`, `.env`, OCI credentials, and sometimes wallet files.
- Notebooks are teaching assets; scripts are usually better for quick verification.
