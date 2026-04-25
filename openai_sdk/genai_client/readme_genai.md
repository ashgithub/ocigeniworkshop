# Welcome to the GenAI Client Module

This module explores the OpenAI-compatible Responses API using OCI-backed configuration. It is designed as a beginner-friendly walkthrough that starts with simple calls and progressively introduces streaming, structured outputs, tool calling, multimodal inputs, code execution tools, MCP integration, and tracing.

If you are new to this codebase, the key idea is: every script shows one capability clearly, with minimal setup, so you can learn by running small examples end-to-end.

## What You Will Learn

In this module, you will learn how to:

1. Send basic Responses API requests and read plain-text outputs
2. Stream token deltas for real-time UI or CLI rendering
3. Parse structured outputs into typed `pydantic` models
4. Implement manual function-calling loops with local tool execution and `previous_response_id`
5. Use built-in tools such as `web_search`, `image_generation`, `mcp`, and `code_interpreter`
6. Send multimodal inputs (image + text and file + text)
7. Configure reasoning settings and inspect structured output blocks
8. Trace requests with a Langfuse OpenAI-compatible client wrapper

These examples use `OpenAIClientProvider` so requests run against OCI OpenAI-compatible endpoints while keeping the same OpenAI SDK patterns.

## Environment Setup

- `sandbox.yaml`: Stores OCI endpoint/project/compartment/profile settings used by `openai_client_provider.py`.
- `.env`: Optional runtime variables for scripts that read environment values.
- Ensure your OCI authentication and project access are correctly configured before running examples.

Common environment values used across this folder:

- `LLM_SERVICE_ENDPOINT`
- `OPENAI_API_KEY`
- `OCI_OPENAI_PROJECT`
- `OCI_COMPARTMENT_ID`
- `OCI_PROFILE`

Additional variables for specific scripts:

- `OCI_GENAI_API_KEY`, `OCI_GENAI_PROJECT_ID` (`langfuse_client.py`)

How to run files from project root:

- Preferred pattern: `uv run python -m openai_sdk.genai_client.<script_name_without_py>`
- Example: `uv run python -m openai_sdk.genai_client.base_client`

## Suggested Study Order and File Descriptions

The files are designed to build on each other. Follow this order for the smoothest beginner path:

1. **`base_client.py`**: Starts with the two most important patterns: one normal `responses.create` call and one streaming call.
   - Key features: Non-streaming + streaming in one file, minimal setup.
   - How to run: `uv run python -m openai_sdk.genai_client.base_client`.
   - Why first: It gives you the baseline mental model for every later script.

2. **`streaming.py`**: Focused streaming-only example that prints token deltas as they arrive.
   - Key features: Event-loop style output rendering from `response.output_text.delta` chunks.
   - How to run: `uv run python -m openai_sdk.genai_client.streaming`.
   - Why second: Helps you understand real-time output handling before adding complexity.

3. **`structured_response.py`**: Parses model output directly into a typed `pydantic` class (`CalendarEvent`).
   - Key features: `responses.parse`, schema validation, strongly-typed outputs.
   - How to run: `uv run python -m openai_sdk.genai_client.structured_response`.
   - Why here: Structured outputs are foundational for reliable app logic.

4. **`reasoning.py`**: Shows reasoning controls (`effort`, `summary`) and how to inspect raw output blocks.
   - Key features: Reasoning configuration and output introspection via serialized JSON.
   - How to run: `uv run python -m openai_sdk.genai_client.reasoning`.
   - Why here: Builds on basic calls and helps you inspect advanced model behavior.

5. **`api_state.py`**: Demonstrates manual function calling flow with a local Python tool.
   - Key features: Function schema declaration, tool-call detection, local execution, `previous_response_id` continuation.
   - How to run: `uv run python -m openai_sdk.genai_client.api_state`.
   - Why here: Introduces app-like control flow where your code and model collaborate.

6. **`web_search.py`**: Uses built-in `web_search` for prompts that need current information.
   - Key features: Tool-enabled Responses API request with minimal changes to normal request flow.
   - How to run: `uv run python -m openai_sdk.genai_client.web_search`.
   - Why here: Easiest built-in tool to understand after manual function calling.

7. **`image_generator.py`**: Uses `image_generation` tool and saves output image bytes to disk.
   - Key features: Tool call output extraction and base64 decoding to local file.
   - How to run: `uv run python -m openai_sdk.genai_client.image_generator`.
   - Why here: Demonstrates non-text output handling.

8. **`multimodal.py`**: Sends image+text and file+text inputs in the same script.
   - Key features: Local image encoding, file upload (`purpose="user_data"`), mixed-content prompts.
   - How to run: `uv run python -m openai_sdk.genai_client.multimodal`.
   - Why here: Multimodal patterns are easier after text and tool fundamentals.

9. **`mcp_client.py`**: Connects a remote MCP server as a tool in Responses API.
   - Key features: Remote tool provider via MCP server URL and model-side tool calling.
   - How to run: `uv run python -m openai_sdk.genai_client.mcp_client`.
   - Why here: Introduces external tool ecosystems beyond local code.

10. **`code_interpreter.py`**: Demonstrates `code_interpreter` with auto containers and a named container.
   - Key features: Container configuration (`auto`, memory limits, explicit container reuse), tool-required execution.
   - How to run: `uv run python -m openai_sdk.genai_client.code_interpreter`.
   - Why here: Most advanced tool flow in this folder.

11. **`langfuse_client.py`**: Uses Langfuse OpenAI-compatible wrapper for traced requests.
   - Key features: Traceable Responses API call, optional MCP tool with Langfuse client.
   - How to run: `uv run python -m openai_sdk.genai_client.langfuse_client`.
   - Why last: Requires extra external setup and is easiest once core patterns are familiar.

12. **`genai_client.ipynb`**: Notebook version of the walkthrough for interactive learning.
   - Key features: Hands-on experimentation and step-by-step execution in cells.
   - How to run: Open in Jupyter or VS Code and run cells in order.

## Project Ideas

Here are practical projects you can build after completing this module:

1. **Build a grounded assistant with optional web search**:
   - Start with normal Responses calls and enable `web_search` only when freshness is needed.
   - Add a switch that compares outputs with and without search.

2. **Create a structured extraction pipeline**:
   - Use `structured_response.py` patterns to extract entities/events from unstructured text.
   - Validate with `pydantic` and store outputs in a database.

3. **Implement a tool-calling weather or finance assistant**:
   - Extend `api_state.py` with real external APIs.
   - Add fallback behavior when tool calls fail.

4. **Build a multimodal document helper**:
   - Use `multimodal.py` to accept PDFs/images and produce summaries or action items.
   - Save extracted insights in JSON using structured outputs.

5. **Create a code-analysis helper with code interpreter**:
   - Use `code_interpreter.py` patterns for calculations, transformations, and quick data analysis.
   - Reuse named containers for related tasks in one session.

## Resources and Links

- **Documentation**:
  - [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
  - [Streaming Responses Guide](https://platform.openai.com/docs/guides/streaming-responses)
  - [Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)
  - [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
  - [Tools Guide](https://platform.openai.com/docs/guides/tools)
  - [Web Search Tool](https://platform.openai.com/docs/guides/tools-web-search)
  - [Code Interpreter Tool](https://platform.openai.com/docs/guides/tools-code-interpreter)
  - [Remote MCP Tooling](https://platform.openai.com/docs/guides/tools-remote-mcp)
  - [Images and Vision Guide](https://platform.openai.com/docs/guides/images-vision)
  - [Langfuse Python SDK](https://langfuse.com/docs/sdk/python/overview)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas and share implementations.
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
  - **#generative-ai-users**: Questions about OCI Gen AI and model capabilities.
  - **#genai-hosted-deployment-users**: GA deployment and integration updates.
