# Agent SDK Learning Guide

This folder contains beginner-friendly, incremental examples for learning the OpenAI Agents SDK with your OCI-backed client setup.

## What You Will Learn

1. Build and run a minimal agent.
2. Stream tokens in real time.
3. Return typed structured outputs.
4. Register and use function tools.
5. Keep multi-turn memory.
6. Route requests with agent handoffs.
7. Add input guardrails.
8. Require human approval for sensitive tool calls.
9. Run a basic voice pipeline and save WAV output.

## Prerequisites

1. Dependencies installed with `uv`.
2. `.env` configured (copy from `.env.example` at project root).
3. OCI/OpenAI-compatible values available so `OpenAIClientProvider` can initialize.

Common environment variables used by examples:

- `LLM_SERVICE_ENDPOINT`
- `OPENAI_API_KEY`
- `OCI_OPENAI_PROJECT`
- `OCI_COMPARTMENT_ID`
- `OCI_PROFILE`

Optional variables for voice examples:

- `VOICE_STT_MODEL`
- `VOICE_TTS_MODEL`
- `VOICE_OUTPUT_FILE`

## How To Run

Run from project root:

```bash
uv run python -m openai_sdk.agent_sdk.simple_agent
uv run python -m openai_sdk.agent_sdk.streaming_agent
uv run python -m openai_sdk.agent_sdk.structured_agent
uv run python -m openai_sdk.agent_sdk.use_tool
uv run python -m openai_sdk.agent_sdk.multiturn
uv run python -m openai_sdk.agent_sdk.orchestration
uv run python -m openai_sdk.agent_sdk.guardail
uv run python -m openai_sdk.agent_sdk.guardail_approval
uv run python -m openai_sdk.agent_sdk.voice_agent
```

## File-by-File Guide

- `simple_agent.py`: Minimal one-agent, one-prompt flow.
- `streaming_agent.py`: Streaming response deltas as they arrive.
- `structured_agent.py`: Structured output using `pydantic.BaseModel`.
- `use_tool.py`: Function tool registration and agent tool-calling behavior.
- `multiturn.py`: Local session memory (`SQLiteSession`) and server-linked turns (`previous_response_id`).
- `orchestration.py`: Triage agent with handoffs to specialists.
- `guardail.py`: Input guardrail that blocks selected requests.
- `guardail_approval.py`: Human-in-the-loop tool approval interruptions.
- `voice_agent.py`: Voice pipeline (STT + agent workflow + TTS) and WAV output.
- `agent_sdk.ipynb`: Guided notebook with all major patterns and practice prompts.
- `__init__.py`: Package marker.

## Recommended Learning Order

1. `simple_agent.py`
2. `streaming_agent.py`
3. `structured_agent.py`
4. `use_tool.py`
5. `multiturn.py`
6. `orchestration.py`
7. `guardail.py`
8. `guardail_approval.py`
9. `voice_agent.py`
10. `agent_sdk.ipynb`

## Notebook Coverage

`agent_sdk.ipynb` includes guided sections for:

- Setup and environment initialization
- Minimal agent run
- Streaming events
- Structured output parsing
- Tool usage
- Multi-turn memory patterns
- Orchestration handoffs
- Input guardrails
- Approval interruptions
- Practice experiments and discussion prompts

## Safe Experiments

1. Change one variable at a time (prompt, instructions, model) and compare behavior.
2. Add a second tool and update instructions so the model chooses between tools.
3. Expand structured schemas with optional fields.
4. Tune guardrail classifier instructions and observe false positives/negatives.
5. Add another specialist to orchestration and test routing quality.

## Troubleshooting

- Auth errors: Verify `.env` values and OCI profile availability.
- Model errors: Confirm the selected model is available in your configured project/endpoint.
- Voice output missing: Check voice model access and try overriding `VOICE_STT_MODEL` / `VOICE_TTS_MODEL`.

## References

- OpenAI Agents SDK docs: https://openai.github.io/openai-agents-python/
- OpenAI Agents guides: https://developers.openai.com/api/docs/guides/agents
- Pydantic docs: https://docs.pydantic.dev/
- Local OCI client configuration: `openai_client_provider.py`
