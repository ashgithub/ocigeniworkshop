""" What this file does:
Demonstrates how to stream model tokens in real time.
Instead of waiting for one final answer, this prints deltas as they arrive.

Documentation for reference:
- OpenAI SDK Streaming: https://developers.openai.com/api/docs/guides/streaming-responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code
- #genai-hosted-deployment-users: Information on GA deployment and integrations

Environment setup:
- Use `.env.example` to create your local `.env`
- Ensure OCI/OpenAI endpoint and project values are configured
- Confirm your OCI profile is available in the environment

How to run the file:
uv run python agent_sdk/streaming_agent.py

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
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 3: Start a streamed run.
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


if __name__ == "__main__":
    asyncio.run(main())
