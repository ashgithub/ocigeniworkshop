# OpenAI SDK Module

This directory contains examples for two tracks:

1. `agent_sdk`: OpenAI Agents SDK patterns (agents, tools, orchestration, guardrails, approvals, voice)
2. `genai_client`: OpenAI-compatible Responses API patterns (streaming, structured outputs, state continuation, built-in tools, multimodal)

All examples are configured to run with OCI-backed OpenAI-compatible clients via `openai_client_provider.py`.

## What You Will Learn

This module covers the following topics:

1. Creating a basic agent and running a single prompt
2. Streaming response deltas in real time (Agents SDK and Responses API styles)
3. Returning typed structured outputs with `pydantic`
4. Registering and using function tools
5. Preserving context/state across multi-turn conversations
6. Routing requests between specialist agents with handoffs
7. Applying input guardrails to block selected requests
8. Requiring human approval for sensitive tool calls
9. Running a basic voice pipeline and saving WAV output
10. Using built-in tools (`web_search`, `mcp`, `code_interpreter`, `image_generation`)
11. Running multimodal inputs (image + text, file + text)

OCI Generative AI provides OpenAI-compatible APIs that support features such as structured output, function calling, orchestration, and built-in tools. These examples use `OpenAIClientProvider` so the SDK runs with OCI-backed configuration.

## Environment Setup

- `sandbox.yaml`: Contains OCI configuration values used by `openai_client_provider.py`.
- Ensure you have access to OCI Generative AI services and valid authentication before running the examples.

Important keys are the use of a **valid project ID** and the right **OCI profile** from config file, values by default on the `sandbox.yaml` are enough to run all examples.

## Langfuse set up

Some examples in this folder use Langfuse for tracing.

1. create an account at https://langfuse.com/?tab=metrics
2. create an demo org & project
3. create your API keys
4. Set the .env file variables: LANGFUSE_HOST, LANGFUSE_SK, LANGFUSE_PK
5. refer to [OpenAI Agents Langfuse Integration](https://langfuse.com/integrations/frameworks/openai-agents) for details

See `genai_client/langfuse_client.py` for a basic example on using langfuse tracing.

> [!Important]
> To use lagfuse snippet, requires >=4.5.1 package version.
> For compatibility on other snippets, global version is on 3.9.1.
> Upgrade or use in a new environment for running.

## Suggested Study Order

The examples shows different capabilities for agents and genai clients

`output` folder keeps the examples for multimodal examples and image/audio generation.

1. **`agent_sdk/agent_sdk.ipynb`**
   - Guided notebook walkthrough of core Agent SDK patterns
   - Covers minimal agent runs, streaming, tools, orchestration, guardrails, approvals, and voice

2. **`agent_sdk/simple_agent.py`**
   - Minimal one-agent, one-prompt flow

3. **`agent_sdk/streaming_agent.py`**
   - Streamed token deltas with `Runner.run_streamed`

4. **`agent_sdk/structured_agent.py`**
   - Structured output parsing into a typed `pydantic` model

5. **`agent_sdk/use_tool.py`**
   - Function tool registration and tool-calling behavior

6. **`agent_sdk/multiturn.py`**
   - Multi-turn memory with `SQLiteSession` and `previous_response_id`

7. **`agent_sdk/orchestration.py`**
   - Triage and handoffs between specialist agents

8. **`agent_sdk/guardail.py`**
   - Input guardrails and tripwire handling

9. **`agent_sdk/guardail_approval.py`**
   - Human-in-the-loop approvals for sensitive tool calls

10. **`agent_sdk/voice_agent.py`**
   - Voice pipeline (STT + agent + TTS) with WAV output

11. **`genai_client/genai_client.ipynb`**
   - Guided notebook for Responses API and tool usage patterns

12. **`genai_client/base_client.py`**
   - Minimal request/response and basic streaming calls

13. **`genai_client/streaming.py`**
   - Focused streaming example with text deltas

14. **`genai_client/structured_response.py`**
   - Typed parsing with `pydantic.BaseModel`

15. **`genai_client/api_state.py`**
   - Manual function-calling loop and state continuation

16. **`genai_client/web_search.py`**
   - Built-in `web_search` tool usage

17. **`genai_client/multimodal.py`**
   - Image+text and file+text examples

18. **`genai_client/image_generator.py`**
   - Image generation and local file save

19. **`genai_client/mcp_client.py`**
   - Remote MCP integration

20. **`genai_client/code_interpreter.py`**
   - Code interpreter container examples

21. **`genai_client/langfuse_client.py`**
   - Optional Langfuse tracing flow

## Running

RIGHT command pattern to run from project root:
uv run python -m openai_sdk.<subfolder>.<script_name_without_py>

Examples:
- uv run python -m openai_sdk.agent_sdk.simple_agent
- uv run python -m openai_sdk.genai_client.base_client

## Slack Channels

- `#generative-ai-users`: Questions about OCI Generative AI
- `#igiu-innovation-lab`: General project discussions
- `#igiu-ai-learning`: Help with the sandbox environment or workshop examples
- `#genai-hosted-deployment-users`: Information on GA deployment and integrations
