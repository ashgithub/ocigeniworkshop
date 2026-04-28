# Welcome to the GenAI Client Module

This module explores Large Language Model capabilities using the OpenAI-compatible Responses API with OCI-backed authentication and endpoint configuration. It covers foundational request patterns, streaming, structured outputs, reasoning controls, tool calling, multimodal inputs, remote MCP integration, code interpreter usage, and optional Langfuse tracing.

OCI Generative AI provides OpenAI-compatible APIs that support modern features such as structured outputs, built-in tools, function calling, and response-state continuation. These examples use `OpenAIClientProvider` so the same client setup is reused across scripts.

## What You Will Learn

In this module, you will learn how to:

1. Send basic Responses API requests and read output text
2. Stream token deltas for real-time rendering
3. Parse structured output into `pydantic` models
4. Configure reasoning settings and inspect response output blocks
5. Handle manual tool-calling loops with `previous_response_id`
6. Use built-in tools (`web_search`, `image_generation`, `mcp`, `code_interpreter`)
7. Send multimodal requests (image + text, file + text)
8. Add tracing with a Langfuse OpenAI-compatible wrapper

## Environment Setup

- `sandbox.yaml`: Required. This is the main configuration source for these examples.
- `.env`: used only for the langfuse set up, described below.
- Ensure OCI profile, compartment, and project values in `sandbox.yaml` are valid.

For most files in `openai_sdk/genai_client`, no additional environment variables are required beyond valid `sandbox.yaml` configuration.

Run commands from project root using:

- `uv run python -m openai_sdk.genai_client.<script_name_without_py>`

Example:

- `uv run python -m openai_sdk.genai_client.base_client`

## Langfuse Setup

`langfuse_client.py` demonstrates the Langfuse OpenAI wrapper pattern. If you want traces to appear in a Langfuse project, configure Langfuse credentials.

1. Create a Langfuse account and project.
2. Set Langfuse environment variables:
   - `LANGFUSE_PUBLIC_KEY`
   - `LANGFUSE_SECRET_KEY`
   - `LANGFUSE_BASE_URL` (for region/self-host)
3. Run:
   - `uv run python -m openai_sdk.genai_client.langfuse_client`

## Suggested Study Order and File Descriptions

The files are designed to build on one another. Study them in this order for a progressive understanding:

1. **`base_client.py`**: Demonstrates baseline Responses API usage with one normal call and one streaming call.
   - Key features: `responses.create`, plain output text, initial streaming pattern.
   - How to run: `uv run python -m openai_sdk.genai_client.base_client`.
   - Docs: [Responses API](https://platform.openai.com/docs/api-reference/responses), [Streaming Responses](https://platform.openai.com/docs/guides/streaming-responses).

2. **`streaming.py`**: Focused streaming-only walkthrough for token delta handling.
   - Key features: event iteration and incremental output rendering.
   - How to run: `uv run python -m openai_sdk.genai_client.streaming`.
   - Docs: [Streaming Responses](https://platform.openai.com/docs/guides/streaming-responses).

3. **`structured_response.py`**: Demonstrates typed parsing with a `pydantic` schema.
   - Key features: `responses.parse`, validation into Python objects.
   - How to run: `uv run python -m openai_sdk.genai_client.structured_response`.
   - Docs: [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs).

4. **`reasoning.py`**: Demonstrates reasoning controls and structured output inspection.
   - Key features: `reasoning` configuration and output serialization.
   - How to run: `uv run python -m openai_sdk.genai_client.reasoning`.
   - Docs: [Reasoning Guide](https://platform.openai.com/docs/guides/reasoning).

5. **`api_state.py`**: Demonstrates manual function-calling state continuation.
   - Key features: tool schema declaration, local function execution, `previous_response_id` chaining.
   - How to run: `uv run python -m openai_sdk.genai_client.api_state`.
   - Docs: [Function Calling](https://platform.openai.com/docs/guides/function-calling), [Responses API](https://platform.openai.com/docs/api-reference/responses).

6. **`web_search.py`**: Demonstrates built-in web grounding via `web_search`.
   - Key features: tool-enabled call for freshness-sensitive prompts.
   - How to run: `uv run python -m openai_sdk.genai_client.web_search`.
   - Docs: [Tools Guide](https://platform.openai.com/docs/guides/tools), [Web Search Tool](https://platform.openai.com/docs/guides/tools-web-search).

7. **`image_generator.py`**: Demonstrates image generation and local file persistence.
   - Key features: `image_generation` tool call and base64 decode/save.
   - How to run: `uv run python -m openai_sdk.genai_client.image_generator`.
   - Docs: [Image Generation](https://platform.openai.com/docs/guides/image-generation).

8. **`multimodal.py`**: Demonstrates image+text and file+text inputs.
   - Key features: data-URI image input, file upload, mixed-content prompt blocks.
   - How to run: `uv run python -m openai_sdk.genai_client.multimodal`.
   - Docs: [Images and Vision](https://platform.openai.com/docs/guides/images-vision), [PDF and File Inputs](https://platform.openai.com/docs/guides/pdf-files).

9. **`mcp_client.py`**: Demonstrates remote MCP tool integration.
   - Key features: model access to remote MCP server capabilities.
   - How to run: `uv run python -m openai_sdk.genai_client.mcp_client`.
   - Docs: [Remote MCP Tools](https://platform.openai.com/docs/guides/tools-remote-mcp).

10. **`code_interpreter.py`**: Demonstrates code interpreter containers.
   - Key features: auto container, memory configuration, explicit named container use.
   - How to run: `uv run python -m openai_sdk.genai_client.code_interpreter`.
   - Docs: [Code Interpreter Tool](https://platform.openai.com/docs/guides/tools-code-interpreter).

11. **`langfuse_client.py`**: Demonstrates tracing-ready client pattern via Langfuse wrapper.
   - Key features: OpenAI-compatible wrapped client and trace-friendly requests.
   - How to run: `uv run python -m openai_sdk.genai_client.langfuse_client`.
   - Docs: [Langfuse OpenAI (Python)](https://langfuse.com/integrations/model-providers/openai-py).

12. **`genai_client.ipynb`**: Notebook walkthrough covering the same patterns interactively.
   - Key features: cell-by-cell experiments and guided progression.
   - How to run: Open in Jupyter or VS Code and execute sequentially.

## Project Ideas

Here are ideas to extend these examples:

1. **Grounded assistant with optional search**:
   - Start from `base_client.py` + `web_search.py`.
   - Compare answers with and without tool grounding.

2. **Structured extraction service**:
   - Start from `structured_response.py`.
   - Build schemas for events, tickets, or forms and validate results.

3. **Tool-calling workflow service**:
   - Start from `api_state.py`.
   - Replace stub functions with real APIs and maintain response state across turns.

4. **Multimodal document helper**:
   - Start from `multimodal.py`.
   - Accept images/PDFs and return summaries plus structured metadata.

5. **Code-enabled analysis assistant**:
   - Start from `code_interpreter.py`.
   - Reuse named containers for iterative numeric/data tasks.

## Resources and Links

- **Documentation**:
  - [Responses API Reference](https://platform.openai.com/docs/api-reference/responses)
  - [Streaming Responses Guide](https://platform.openai.com/docs/guides/streaming-responses)
  - [Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)
  - [Reasoning Guide](https://platform.openai.com/docs/guides/reasoning)
  - [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
  - [Tools Guide](https://platform.openai.com/docs/guides/tools)
  - [Remote MCP Tools](https://platform.openai.com/docs/guides/tools-remote-mcp)
  - [Code Interpreter Tool](https://platform.openai.com/docs/guides/tools-code-interpreter)
  - [Image Generation Guide](https://platform.openai.com/docs/guides/image-generation)
  - [Images and Vision Guide](https://platform.openai.com/docs/guides/images-vision)
  - [PDF and File Inputs Guide](https://platform.openai.com/docs/guides/pdf-files)
  - [Langfuse OpenAI Integration (Python)](https://langfuse.com/integrations/model-providers/openai-py)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas and implementations.
  - **#igiu-ai-learning**: Help with sandbox environment or running scripts.
  - **#generative-ai-users**: Questions about OCI Generative AI capabilities.
  - **#genai-hosted-deployment-users**: GA deployment and integration updates.
