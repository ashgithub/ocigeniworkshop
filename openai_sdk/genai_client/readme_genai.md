# GenAI Client Learning Guide

This folder contains focused, beginner-friendly examples for the OpenAI-compatible Responses API and OCI integrations.

## What You Will Learn

1. Basic request/response calls.
2. Streaming token deltas.
3. Structured output parsing with `pydantic`.
4. Manual function-calling state continuation.
5. Built-in tools (`web_search`, `mcp`, `code_interpreter`, `image_generation`).
6. Multimodal inputs (image + text, file + text).
7. Optional tracing flow with Langfuse.

## Prerequisites

1. Install dependencies with `uv sync`.
2. Configure `.env` in project root (copy from `.env.example`).
3. Ensure OCI profile and endpoint/project values are valid.

Common environment variables used in this folder:

- `LLM_SERVICE_ENDPOINT`
- `OPENAI_API_KEY`
- `OCI_OPENAI_PROJECT`
- `OCI_COMPARTMENT_ID`
- `OCI_PROFILE`

Additional variables for specific scripts:

- `OCI_GENAI_API_KEY` and `OCI_GENAI_PROJECT_ID` for `langfuse_client.py`

## How To Run

Run from project root:

```bash
uv run python genai_client/base_client.py
uv run python genai_client/streaming.py
uv run python genai_client/reasoning.py
uv run python genai_client/structured_response.py
uv run python genai_client/api_state.py
uv run python genai_client/web_search.py
uv run python genai_client/multimodal.py
uv run python genai_client/image_generator.py
uv run python genai_client/mcp_client.py
uv run python genai_client/code_interpreter.py
uv run python genai_client/langfuse_client.py
```

Optional advanced examples:

```bash
uv run python genai_client/skills_use/skill_injection.py
uv run python genai_client/skills_use/skill_as_function.py
uv run python genai_client/skills_use/tool_search_skill.py
uv run python genai_client/vector_store/file_search.py
uv run python genai_client/vector_store/vector_store.py
uv run python genai_client/vector_store/nl2sql.py
```

## Main File Guide

- `base_client.py`: Minimal standard and streaming Responses API calls.
- `streaming.py`: Focused streaming example with text deltas.
- `reasoning.py`: Reasoning settings and raw output inspection.
- `structured_response.py`: Typed parsing into `BaseModel`.
- `api_state.py`: Manual function call loop with `previous_response_id`.
- `web_search.py`: Built-in `web_search` tool example.
- `multimodal.py`: Image+text and file+text inputs.
- `image_generator.py`: Generate image output and save locally.
- `mcp_client.py`: Remote MCP tool integration.
- `code_interpreter.py`: Auto and named containers for Python tool execution.
- `langfuse_client.py`: Responses request via Langfuse OpenAI-compatible client.
- `genai_client.ipynb`: Guided notebook with runnable patterns and exercises.
- `__init__.py`: Package marker.

## Recommended Learning Order

1. `base_client.py`
2. `streaming.py`
3. `structured_response.py`
4. `api_state.py`
5. `web_search.py`
6. `multimodal.py`
7. `image_generator.py`
8. `mcp_client.py`
9. `code_interpreter.py`
10. `langfuse_client.py`
11. `genai_client.ipynb`

## Safe Experiments

1. Change one variable at a time (prompt, model, tool).
2. Compare the same prompt across two model IDs.
3. Add fields to tool schemas in `api_state.py`.
4. Switch `web_search` on/off and compare grounding quality.
5. Swap image/file inputs in `multimodal.py` and compare outputs.

## Troubleshooting

- Auth failures: verify `.env` values and OCI profile availability.
- Model failures: ensure the model ID is enabled in your project/endpoint.
- Tool failures: confirm your environment has access to the required tool capability.
- File input failures: confirm local files exist and are readable.

## References

- Responses API docs: https://platform.openai.com/docs/api-reference/responses
- Tools guide: https://platform.openai.com/docs/guides/tools
- Structured outputs guide: https://platform.openai.com/docs/guides/structured-outputs
- OpenAI Agents Python SDK docs: https://openai.github.io/openai-agents-python/
