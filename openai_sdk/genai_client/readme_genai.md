# Welcome to the GenAI Client Module

This module explores Large Language Model capabilities using the OpenAI-compatible Responses API with OCI-backed authentication and endpoint configuration.

It includes:

1. Core response patterns (basic calls, streaming, structured outputs, reasoning).
2. Built-in tools and multimodal input patterns.
3. Advanced modules for containers, memory, and vector store retrieval workflows.
4. Optional tracing with Langfuse.

OCI Generative AI provides OpenAI-compatible APIs that support structured outputs, built-in tools, function calling, and response-state continuation. These examples use `OpenAIClientProvider` so one client setup pattern can be reused across scripts.

## What You Will Learn

In this module, you will learn how to:

1. Send basic Responses API requests and read output text.
2. Stream token deltas for real-time rendering.
3. Parse structured output into `pydantic` models.
4. Configure reasoning settings and inspect response output blocks.
5. Handle manual tool-calling loops with `previous_response_id`.
6. Use built-in tools (`web_search`, `image_generation`, `mcp`, `code_interpreter`, `file_search`).
7. Send multimodal requests (image + text, file + text).
8. Work with container lifecycle and container file operations.
9. Test conversation memory behaviors and access policies.
10. Build vector store and retrieval workflows, including semantic search and batching.
11. Extend to connector-based ingestion and NL2SQL generation.
12. Add tracing with a Langfuse OpenAI-compatible wrapper.

## Environment Setup

- `sandbox.yaml`: Required. Main configuration source for these examples.
- `.env`: Used only for Langfuse examples.
- Ensure OCI profile, compartment, and project values in `sandbox.yaml` are valid.

For most files in `openai_sdk/genai_client`, no additional environment variables are required beyond valid `sandbox.yaml` configuration.

Run commands from project root using:

- `uv run openai_sdk/genai_client/<script_name>.py`

## Folder Breakdown

This folder is organized by learning layers. Start at top-level core examples, then move into focused submodules.

1. **Core request patterns (top-level files)**
   - `base_client.py`, `streaming.py`, `structured_response.py`, `reasoning.py`, `api_state.py`.
   - Focus: baseline Responses API, streaming, schemas, reasoning, function-loop state handling.

2. **Built-in tools and multimodal (top-level files)**
   - `web_search.py`, `image_generator.py`, `mcp_client.py`, `code_interpreter.py`, `multimodal.py`.
   - Focus: tool usage, multimodal input handling, remote MCP, code interpreter interactions.

3. **Containers module (`containers/`)**
   - Focus: container resource lifecycle and container file operations.
   - Entry point: `containers/readme_containers.md`.

4. **Memory module (`memory/`)**
   - Focus: memory subject sharing, access policies, and optimization metadata.
   - Entry point: `memory/readme_memory.md`.

5. **Vector store module (`vector_store/`)**
   - Focus: files + vector stores, semantic search, batch ingestion, connectors, NL2SQL.
   - Entry point: `vector_store/readme_vector_store.md`.

6. **Observability and notebook walkthroughs**
   - `langfuse_client.py`, `genai_client.ipynb` plus module-specific notebooks.

## Suggested Study Order and File Descriptions

The files are designed to build progressively from core API usage to advanced retrieval/memory workflows.

1. **`base_client.py`**
   - Demonstrates baseline Responses API usage with one normal call and one streaming call.
   - Run: `uv run openai_sdk/genai_client/base_client.py`.

2. **`streaming.py`**
   - Focused streaming walkthrough for token delta handling.
   - Run: `uv run openai_sdk/genai_client/streaming.py`.

3. **`structured_response.py`**
   - Demonstrates typed parsing with a `pydantic` schema via `responses.parse`.
   - Run: `uv run openai_sdk/genai_client/structured_response.py`.

4. **`reasoning.py`**
   - Demonstrates reasoning controls and output block inspection.
   - Run: `uv run openai_sdk/genai_client/reasoning.py`.

5. **`api_state.py`**
   - Demonstrates manual function-calling and `previous_response_id` continuation.
   - Run: `uv run openai_sdk/genai_client/api_state.py`.

6. **`web_search.py`**
   - Demonstrates built-in `web_search` grounding.
   - Run: `uv run openai_sdk/genai_client/web_search.py`.

7. **`image_generator.py`**
   - Demonstrates image generation tool usage and local save.
   - Run: `uv run openai_sdk/genai_client/image_generator.py`.

8. **`multimodal.py`**
   - Demonstrates image+text and file+text requests.
   - Run: `uv run openai_sdk/genai_client/multimodal.py`.

9. **`mcp_client.py`**
   - Demonstrates remote MCP integration.
   - Run: `uv run openai_sdk/genai_client/mcp_client.py`.

10. **`code_interpreter.py`**
   - Demonstrates code interpreter containers and reuse patterns.
   - Run: `uv run openai_sdk/genai_client/code_interpreter.py`.

11. **`containers/readme_containers.md`**
   - Read this first for container-focused workflows.
   - Then run:
     - `uv run openai_sdk/genai_client/containers/base_example.py`
     - `uv run openai_sdk/genai_client/containers/container_files.py`

12. **`memory/readme_memory.md`**
   - Read this first for memory policy and subject workflows.
   - Then run:
     - `uv run openai_sdk/genai_client/memory/memory_subject.py`
     - `uv run openai_sdk/genai_client/memory/memory_access.py`
     - `uv run openai_sdk/genai_client/memory/memory_optimization.py`

13. **`vector_store/readme_vector_store.md`**
   - Read this first for vector retrieval workflows.
   - Then run module scripts in the order listed in that README.

14. **`langfuse_client.py`**
   - Demonstrates tracing-ready client usage via Langfuse wrapper.
   - Run: `uv run openai_sdk/genai_client/langfuse_client.py`.

15. **`genai_client.ipynb`**
   - Notebook walkthrough that complements the script-based path.

## Module Readmes

For complete submodule guidance, use:

- `openai_sdk/genai_client/containers/readme_containers.md`
- `openai_sdk/genai_client/memory/readme_memory.md`
- `openai_sdk/genai_client/vector_store/readme_vector_store.md`

## Langfuse Setup

`langfuse_client.py` demonstrates the Langfuse OpenAI wrapper pattern. If you want traces to appear in a Langfuse project, configure credentials:

1. Create a Langfuse account and project.
2. Set environment variables:
   - `LANGFUSE_PUBLIC_KEY`
   - `LANGFUSE_SECRET_KEY`
   - `LANGFUSE_BASE_URL` (for region/self-host)
3. Run:
   - `uv run openai_sdk/genai_client/langfuse_client.py`

## Project Ideas

1. **Grounded assistant with optional search**
   - Start from `base_client.py` + `web_search.py`.

2. **Structured extraction service**
   - Start from `structured_response.py`.

3. **Tool-calling workflow service**
   - Start from `api_state.py` and replace stub tools with real APIs.

4. **Multimodal document helper**
   - Start from `multimodal.py` and add document schemas.

5. **Memory-aware assistant**
   - Start from `memory/memory_subject.py` and `memory/memory_access.py`.

6. **Enterprise retrieval assistant**
   - Start from `vector_store/vector_api.py` and `vector_store/file_search.py`.

## Resources and Links

- [Responses API Reference](https://platform.openai.com/docs/api-reference/responses)
- [Streaming Responses Guide](https://platform.openai.com/docs/guides/streaming-responses)
- [Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)
- [Reasoning Guide](https://platform.openai.com/docs/guides/reasoning)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Tools Guide](https://platform.openai.com/docs/guides/tools)
- [File Search Guide](https://platform.openai.com/docs/guides/tools-file-search)
- [Vector Stores API](https://platform.openai.com/docs/api-reference/vector-stores)
- [Containers API](https://platform.openai.com/docs/api-reference/containers)
- [Container Files API](https://platform.openai.com/docs/api-reference/container-files)
- [Conversations API](https://platform.openai.com/docs/api-reference/conversations)
- [Remote MCP Tools](https://platform.openai.com/docs/guides/tools-remote-mcp)
- [Code Interpreter Tool](https://platform.openai.com/docs/guides/tools-code-interpreter)
- [Image Generation Guide](https://platform.openai.com/docs/guides/image-generation)
- [Images and Vision Guide](https://platform.openai.com/docs/guides/images-vision)
- [PDF and File Inputs Guide](https://platform.openai.com/docs/guides/pdf-files)
- [Langfuse OpenAI Integration (Python)](https://langfuse.com/integrations/model-providers/openai-py)

## Slack Channels

- **#igiu-innovation-lab**: Discuss project ideas and implementations.
- **#igiu-ai-learning**: Help with sandbox environment or running scripts.
- **#generative-ai-users**: Questions about OCI Generative AI capabilities.
- **#genai-hosted-deployment-users**: GA deployment and integration updates.
