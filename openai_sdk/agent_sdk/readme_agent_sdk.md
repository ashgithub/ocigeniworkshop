# Welcome to the Agent SDK Module

This module explores the OpenAI Agents SDK using OCI-backed OpenAI-compatible configuration. It is a beginner-friendly, progressive track that starts with one minimal agent and then adds streaming, structured outputs, tools, multi-turn memory, orchestration handoffs, safety guardrails, approval interruptions, and voice workflows.

OCI Generative AI provides OpenAI-compatible APIs that support agent patterns such as tool calling, handoffs, guardrails, and conversation state. These examples use `OpenAIClientProvider().configure_agents_oci_env()` so every script shares the same OCI-backed setup.

## What You Will Learn

In this module, you will learn how to:

1. Create and run a minimal agent with `Agent` and `Runner`
2. Stream token deltas in real time
3. Return typed structured outputs with `pydantic`
4. Register and use function tools
5. Keep multi-turn context with local and server-linked memory patterns
6. Route requests to specialist agents with handoffs
7. Apply input guardrails before main-agent execution
8. Require human approval for sensitive tool calls
9. Run a basic voice pipeline (STT -> agent -> TTS) and save WAV output

## Environment Setup

- `sandbox.yaml`: Required. This is the main configuration source for these examples.
- `.env`: Optional for most scripts in this folder.
- Ensure `sandbox.yaml` has valid OCI profile, project, and compartment values.

Optional variables used by voice examples:

- `VOICE_STT_MODEL`
- `VOICE_TTS_MODEL`
- `VOICE_OUTPUT_FILE`

Run commands from project root using:

- `uv run python -m openai_sdk.agent_sdk.<script_name_without_py>`

Example:

- `uv run python -m openai_sdk.agent_sdk.simple_agent`

## Suggested Study Order and File Descriptions

The files are designed to build on one another. Study them in this order for a progressive understanding:

1. **`simple_agent.py`**: Smallest end-to-end agent run.
   - Key features: one agent, one prompt, one final response.
   - How to run: `uv run python -m openai_sdk.agent_sdk.simple_agent`.
   - Docs: [Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart), [Agents Overview](https://developers.openai.com/api/docs/guides/agents).

2. **`streaming_agent.py`**: Streams response deltas as they are generated.
   - Key features: streamed events + token-by-token output rendering.
   - How to run: `uv run python -m openai_sdk.agent_sdk.streaming_agent`.
   - Docs: [Running Agents](https://developers.openai.com/api/docs/guides/agents/running-agents), [Streaming Responses](https://platform.openai.com/docs/guides/streaming-responses).

3. **`structured_agent.py`**: Produces typed output validated by a `pydantic` schema.
   - Key features: `output_type` and structured final objects.
   - How to run: `uv run python -m openai_sdk.agent_sdk.structured_agent`.
   - Docs: [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart).

4. **`use_tool.py`**: Adds function tools to an agent.
   - Key features: `@function_tool` and tool-guided response generation.
   - How to run: `uv run python -m openai_sdk.agent_sdk.use_tool`.
   - Docs: [Tools Guide](https://developers.openai.com/api/docs/guides/tools), [Function Calling](https://developers.openai.com/api/docs/guides/function-calling).

5. **`multiturn.py`**: Demonstrates memory across turns.
   - Key features: `SQLiteSession` local memory + `previous_response_id` server-linked continuity.
   - How to run: `uv run python -m openai_sdk.agent_sdk.multiturn`.
   - Docs: [Running Agents](https://developers.openai.com/api/docs/guides/agents/running-agents), [Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart).

6. **`orchestration.py`**: Demonstrates triage and specialist handoffs.
   - Key features: handoff routing across multiple agents.
   - How to run: `uv run python -m openai_sdk.agent_sdk.orchestration`.
   - Docs: [Orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration), [Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart).

7. **`guardail.py`**: Demonstrates input guardrails with tripwire behavior.
   - Key features: classifier guardrail and blocked execution path.
   - How to run: `uv run python -m openai_sdk.agent_sdk.guardail`.
   - Docs: [Guardrails Approvals](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals), [Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart).

8. **`guardail_approval.py`**: Demonstrates human-in-the-loop approvals.
   - Key features: approval interruptions and approve/reject continuation.
   - How to run: `uv run python -m openai_sdk.agent_sdk.guardail_approval`.
   - Docs: [Guardrails Approvals](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals), [Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart).

9. **`voice_agent.py`**: Demonstrates a basic voice workflow with WAV output.
   - Key features: STT + single-agent workflow + TTS stream capture.
   - How to run: `uv run python -m openai_sdk.agent_sdk.voice_agent`.
   - Docs: [Voice Agents](https://developers.openai.com/api/docs/guides/voice-agents), [Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart).

10. **`agent_sdk.ipynb`**: Notebook walkthrough covering the same path interactively.
   - Key features: guided cells for each major pattern.
   - How to run: open in Jupyter/VS Code and execute cells in order.

## Project Ideas

Here are ideas to extend these examples:

1. **Approval-first support assistant**:
   - Start from `use_tool.py` + `guardail_approval.py`.
   - Require explicit operator approval for sensitive actions.

2. **Domain triage assistant**:
   - Start from `orchestration.py`.
   - Add specialist agents and improve routing instructions.

3. **Policy-guarded assistant**:
   - Start from `guardail.py`.
   - Add extra categories and log tripwire decisions.

4. **Memory-aware assistant**:
   - Start from `multiturn.py`.
   - Combine local sessions with structured outputs for tasks/reminders.

5. **Voice FAQ assistant**:
   - Start from `voice_agent.py`.
   - Add domain tools and compare STT/TTS model behavior.

## Resources and Links

- **Documentation**:
  - [Agents Overview](https://developers.openai.com/api/docs/guides/agents)
  - [Agents Quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart)
  - [Running Agents](https://developers.openai.com/api/docs/guides/agents/running-agents)
  - [Orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration)
  - [Guardrails Approvals](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
  - [Tools Guide](https://developers.openai.com/api/docs/guides/tools)
  - [Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
  - [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
  - [Voice Agents](https://developers.openai.com/api/docs/guides/voice-agents)
  - [Streaming Responses](https://platform.openai.com/docs/guides/streaming-responses)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas and implementations.
  - **#igiu-ai-learning**: Help with sandbox environment or running scripts.
  - **#generative-ai-users**: Questions about OCI Generative AI capabilities.
  - **#genai-hosted-deployment-users**: GA deployment and integration updates.
