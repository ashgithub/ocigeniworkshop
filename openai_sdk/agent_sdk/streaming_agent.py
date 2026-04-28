""" What this file does:
Demonstrates how to stream model tokens in real time.
Instead of waiting for one final answer, this prints deltas as they arrive.

Documentation for reference:
- OpenAI Agents SDK Running agents: https://openai.github.io/openai-agents-python/running_agents/
- Streaming responses guide: https://platform.openai.com/docs/guides/streaming-responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code
- #genai-hosted-deployment-users: Information on GA deployment and integrations

Environment setup:
- Ensure `sandbox.yaml` contains valid OCI profile, project, and compartment values
- `.env` is optional for this script
- Ensure you have access to OCI Generative AI services

How to run the file:
uv run python -m openai_sdk.agent_sdk.streaming_agent

Safe experiments:
1. Change USER_PROMPT to a different topic.
2. Remove the short-answer instruction and compare output style.
3. Print all event types to inspect full stream behavior.

Important sections:
1. Step 1: Build a streaming-capable agent.
2. Step 2: Start a streamed run and iterate events.
3. Step 3: Print token deltas and final output. """

import asyncio

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Give me three short facts about Saturn."

def build_planet_guide_agent() -> Agent:
    # Step 1: Create an agent for concise factual answers.
    return Agent(
        name="Planet guide",
        instructions="Answer with short facts.",
        model=MODEL_ID,
    )

async def main() -> None:
    # Step 2: Configure the OpenAI Agents SDK with OCI settings.
    print("Step 2/5: Configuring Agents SDK with OCI-backed client...")
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 3: Start a streamed run.
    print("Step 3/5: Starting streamed run. Tokens will print live:")
    planet_guide = build_planet_guide_agent()
    stream = Runner.run_streamed(planet_guide, USER_PROMPT)

    # Step 4: Print text deltas as they are generated.
    async for event in stream.stream_events():
        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
        ):
            print(event.data.delta, end="", flush=True)

    # Step 5: Print the assembled final output for reference.
    print(f"\nFinal: {stream.final_output}")
    print("Step 5/5: Streaming run completed.")


if __name__ == "__main__":
    asyncio.run(main())
