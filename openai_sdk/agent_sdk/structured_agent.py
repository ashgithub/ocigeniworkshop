""" What this file does:
Demonstrates typed/structured outputs using a Pydantic model.
The agent returns data that is validated into a `CalendarEvent` object.

Documentation for reference:
- OpenAI SDK Structured outputs: https://developers.openai.com/api/docs/guides/structured-outputs
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
uv run python agent_sdk/structured_agent.py

Safe experiments:
1. Add fields to `CalendarEvent` (example: `location: str | None = None`).
2. Try prompts with multiple events and inspect parsed output.
3. Later, change `date` to a stricter type (example: `datetime`).

Important sections:
1. Step 1: Define the structured schema.
2. Step 2: Build an agent with `output_type`.
3. Step 3: Run and print the validated object. """

import asyncio

from agents import Agent, Runner
from pydantic import BaseModel
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Dinner with Priya and Sam on Friday."


class CalendarEvent(BaseModel):
    # Step 1: Schema that the model must populate.
    name: str
    date: str
    participants: list[str]


def build_calendar_extractor_agent() -> Agent:
    # Step 2: Attach the schema through `output_type`.
    return Agent(
        name="Calendar extractor",
        instructions="Extract calendar events from text.",
        model=MODEL_ID,
        output_type=CalendarEvent,
    )


async def main() -> None:
    # Step 3: Configure the OpenAI Agents SDK with OCI settings.
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 4: Run the agent; output is validated into CalendarEvent.
    calendar_extractor = build_calendar_extractor_agent()
    run_result = await Runner.run(calendar_extractor, USER_PROMPT)

    # Step 5: Print the structured object.
    print(run_result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
