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
4. Set the `.env` variables LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY. IMPORTANT set keys to have automatic traces
5. refer to [OpenAI Agents Langfuse Integration](https://langfuse.com/integrations/frameworks/openai-agents) for details

See `genai_client/langfuse_client.py` for a basic example on using langfuse tracing.

## Suggested Study Order

Over here there are information about the main folders and tracks to follow according to the data required.

1. **Connection and environment configuration**
   - `openai_client_provider.py`: Central OCI-backed client configuration used by both tracks.
   - This file is used to connect the OpenAI native api via OCI services
   - Use `oci_openai_client` as instance for genai features such as tool use, mcp and state
   - Use `oci_openai_async_client` as async instance for genai async features such streaming and orchestration.
   - Use `configure_agents_oci_env()` as function call when using the agent features from SDK.
   - Configuration of agent environment is required for guardail, multiturn, orchestration, tools and voice agents.

2. **Pick a learning track based on goal**
   - `agent_sdk/`: For agent workflows (handoffs, guardrails, approvals, voice, tools).
   - `genai_client/`: For direct Responses API workflows (streaming, structured outputs, built-in tools, multimodal).
   - To understand the basic work of the AI features, use `genai_client` for fundamentals on tool usage and direct endpoint calls. Move forward with `agent_sdk` for end-to-end fast plug-in assistant behaivor.

3. **`agent_sdk/` (Agent SDK track overview)**
   - End-to-end assistant behavior using the OpenAI Agents SDK with OCI-backed configuration.
   - Main capability files:
     - `simple_agent.py`, `streaming_agent.py`, `structured_agent.py`: core agent patterns.
     - `use_tool.py`, `multiturn.py`, `orchestration.py`: tools, memory, and handoffs.
     - `guardail.py`, `guardail_approval.py`, `voice_agent.py`: safety, human approvals, and voice pipeline.
   - Entry points for learning:
     - `agent_sdk/readme_agent_sdk.md`: complete beginner walkthrough for this folder.
     - `agent_sdk/agent_sdk.ipynb`: notebook version of the same learning path.

4. **`genai_client/` (Responses API track overview)**
   - Direct OpenAI-compatible Responses API usage patterns, without agent orchestration abstractions.
   - Main capability files:
     - `base_client.py`, `streaming.py`, `structured_response.py`, `reasoning.py`: core request/response patterns.
     - `api_state.py`: manual function-calling flow and `previous_response_id` continuation.
     - `web_search.py`, `image_generator.py`, `mcp_client.py`, `code_interpreter.py`, `multimodal.py`: built-in tools and multimodal features.
     - `langfuse_client.py`: tracing-oriented client usage example.
   - Entry points for learning:
     - `genai_client/readme_genai.md`: complete beginner walkthrough for this folder.
     - `genai_client/genai_client.ipynb`: interactive notebook path.

5. **Support folders and global reference files**
   - `output/`: shared sample artifacts used by demos (image input/output, PDF input, voice WAV output).
   - `openai_client_provider.py`: shared OCI auth + client provider used by both `agent_sdk` and `genai_client`.

## Running

RIGHT command pattern to run from project root:
uv run openai_sdk/<subfolder>/<script_name>.py

Examples:
- uv run openai_sdk/agent_sdk/simple_agent.py
- uv run openai_sdk/genai_client/base_client.py

## Slack Channels

- `#generative-ai-users`: Questions about OCI Generative AI
- `#igiu-innovation-lab`: General project discussions on the lab
- `#igiu-ai-learning`: Help with the sandbox environment or workshop examples, specially on running this repo
- `#genai-hosted-deployment-users`: Information on GA deployment and integrations with new OpenAI SDK
