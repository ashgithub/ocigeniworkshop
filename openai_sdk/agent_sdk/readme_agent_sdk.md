# Welcome to the Agent SDK Module

This module teaches the OpenAI Agents SDK using OCI-backed OpenAI-compatible configuration. It is organized as a progressive walkthrough so beginners can start with one minimal agent and then add more advanced features such as streaming, tools, multi-turn memory, orchestration, guardrails, human approvals, and voice.

If you are new to agent systems, think of this folder as a practical ladder: each script introduces one core capability that builds on the previous one.

## What You Will Learn

In this module, you will learn how to:

1. Create and run a minimal agent with `Agent` + `Runner`
2. Stream token deltas in real time
3. Return typed structured outputs with `pydantic`
4. Register and call Python function tools
5. Keep multi-turn context using local session memory and server-linked turns
6. Route questions to specialist agents with handoffs
7. Add input guardrails that can block unsafe or disallowed requests
8. Require human approval before sensitive tool execution
9. Run a basic voice pipeline (STT -> agent -> TTS) and save WAV output

All scripts use `OpenAIClientProvider().configure_agents_oci_env()` so the OpenAI Agents SDK runs against OCI-backed clients.

## Environment Setup

- `sandbox.yaml`: Stores OCI endpoint/project/compartment/profile values used by `openai_client_provider.py`.
- `.env`: Optional runtime values used by selected scripts.
- Ensure OCI authentication and model access are configured before running examples.

Common values used in this folder:

- `LLM_SERVICE_ENDPOINT`
- `OPENAI_API_KEY`
- `OCI_OPENAI_PROJECT`
- `OCI_COMPARTMENT_ID`
- `OCI_PROFILE`

Optional values for voice workflow:

- `VOICE_STT_MODEL`
- `VOICE_TTS_MODEL`
- `VOICE_OUTPUT_FILE`

How to run files from project root:

- Preferred pattern: `uv run python -m openai_sdk.agent_sdk.<script_name_without_py>`
- Example: `uv run python -m openai_sdk.agent_sdk.simple_agent`

## Suggested Study Order and File Descriptions

These examples are intentionally incremental. Follow this order for the easiest beginner experience:

1. **`simple_agent.py`**: Smallest end-to-end agent run.
   - Key features: One agent, one prompt, one final output.
   - How to run: `uv run python -m openai_sdk.agent_sdk.simple_agent`.
   - Why first: Establishes the core `Agent` + `Runner.run` mental model.

2. **`streaming_agent.py`**: Streams output as it is generated.
   - Key features: `Runner.run_streamed`, event iteration, token delta rendering.
   - How to run: `uv run python -m openai_sdk.agent_sdk.streaming_agent`.
   - Why second: Shows real-time UX pattern used in chat interfaces.

3. **`structured_agent.py`**: Produces validated structured output.
   - Key features: `output_type` with `pydantic.BaseModel` for typed results.
   - How to run: `uv run python -m openai_sdk.agent_sdk.structured_agent`.
   - Why here: Structured outputs are essential for reliable downstream logic.

4. **`use_tool.py`**: Adds function tools to agent behavior.
   - Key features: `@function_tool`, tool registration, instruction-guided tool use.
   - How to run: `uv run python -m openai_sdk.agent_sdk.use_tool`.
   - Why here: Introduces model + code collaboration through tools.

5. **`multiturn.py`**: Demonstrates two memory patterns.
   - Key features: Local memory via `SQLiteSession` and server-linked continuity via `previous_response_id`.
   - How to run: `uv run python -m openai_sdk.agent_sdk.multiturn`.
   - Why here: Multi-turn state is core for real assistants.

6. **`orchestration.py`**: Routes requests with handoffs.
   - Key features: Triage agent delegating to specialist agents.
   - How to run: `uv run python -m openai_sdk.agent_sdk.orchestration`.
   - Why here: Introduces multi-agent coordination patterns.

7. **`guardail.py`**: Applies input guardrails before main handling.
   - Key features: Guardrail classifier agent, tripwire trigger, blocked execution flow.
   - How to run: `uv run python -m openai_sdk.agent_sdk.guardail`.
   - Why here: Adds safety and policy checks to your agent pipeline.

8. **`guardail_approval.py`**: Requires explicit human approval for sensitive tools.
   - Key features: `needs_approval=True`, interruption handling, approve/reject state continuation.
   - How to run: `uv run python -m openai_sdk.agent_sdk.guardail_approval`.
   - Why here: Demonstrates human-in-the-loop controls for high-risk actions.

9. **`voice_agent.py`**: Runs a basic voice workflow and saves WAV output.
   - Key features: STT + single-agent workflow + TTS streaming output to file.
   - How to run: `uv run python -m openai_sdk.agent_sdk.voice_agent`.
   - Why here: Most integrated example in the folder.

10. **`agent_sdk.ipynb`**: Notebook walkthrough covering the full learning path.
   - Key features: Interactive cell-by-cell exploration and easy experimentation.
   - How to run: Open in Jupyter or VS Code and run cells in order.

11. **`__init__.py`**: Package marker for module execution.
   - Key features: Ensures folder behaves as Python package for `-m` runs.

## Project Ideas

After completing this module, you can build:

1. **A customer support assistant with approvals**:
   - Start from `use_tool.py` + `guardail_approval.py`.
   - Require operator confirmation for actions like cancellations or refunds.

2. **A triage tutor with specialist agents**:
   - Extend `orchestration.py` with more specialists (science, coding, writing).
   - Improve handoff instructions and evaluate routing quality.

3. **A safe homework helper**:
   - Build on `guardail.py` to classify and block disallowed request categories.
   - Add audit logging around tripwire events.

4. **A memory-enabled personal assistant**:
   - Use `multiturn.py` patterns to preserve context over multiple turns.
   - Add structured outputs for scheduling, reminders, or task tracking.

5. **A voice-first FAQ assistant**:
   - Use `voice_agent.py` with domain-specific tools.
   - Save audio responses and compare model/voice settings.

## Resources and Links

- **Documentation**:
  - [OpenAI Agents Python SDK](https://openai.github.io/openai-agents-python/)
  - [Agents Guides](https://developers.openai.com/api/docs/guides/agents)
  - [Running Agents](https://developers.openai.com/api/docs/guides/agents/running-agents)
  - [Orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration)
  - [Guardrails](https://developers.openai.com/api/docs/guides/agents/guardrails)
  - [Guardrail Approvals](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
  - [Voice Agents](https://developers.openai.com/api/docs/guides/voice-agents)
  - [Pydantic Models](https://docs.pydantic.dev/)

- **Slack Channels**:
  - **#igiu-innovation-lab**: Discuss project ideas and share implementations.
  - **#igiu-ai-learning**: Help with sandbox environment or running code.
  - **#generative-ai-users**: Questions about OCI Gen AI and model capabilities.
  - **#genai-hosted-deployment-users**: GA deployment and integration updates.
