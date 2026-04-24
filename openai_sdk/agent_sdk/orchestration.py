""" What this file does:
Demonstrates orchestration with handoffs:
a triage agent routes questions to specialist agents.

Documentation for reference:
- OpenAI SDK Orchestration: https://developers.openai.com/api/docs/guides/agents/orchestration
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
uv run python agent_sdk/orchestration.py

Safe experiments:
1. Ask a math question and verify handoff to `Math tutor`.
2. Add a third specialist and update triage instructions.
3. Compare `handoff_description` wording and routing quality.

Important sections:
1. Step 1: Create specialist agents.
2. Step 2: Create triage agent with handoffs.
3. Step 3: Run and inspect which agent responded. """

import asyncio

from agents import Agent, Runner
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Who was the first president of the United States?"

# Step 1: Specialist agent for history questions.
history_tutor = Agent(
    name="History tutor",
    handoff_description="Specialist for history questions.",
    instructions="Answer history questions clearly and concisely.",
    model=MODEL_ID,
)

# Step 2: Specialist agent for math questions.
math_tutor = Agent(
    name="Math tutor",
    handoff_description="Specialist for math questions.",
    instructions="Explain math step by step and include worked examples.",
    model=MODEL_ID,
)

# Step 3: Triage agent that can hand off work to specialists.
triage_agent = Agent(
    name="Homework triage",
    instructions="Route each homework question to the right specialist.",
    model=MODEL_ID,
    handoffs=[history_tutor, math_tutor],
)


async def main() -> None:
    # Step 4: Configure the OpenAI Agents SDK with OCI settings.
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 5: Run the triage agent; it can hand off to a specialist.
    run_result = await Runner.run(triage_agent, USER_PROMPT)

    # Step 6: Print answer and the agent that produced it.
    print(run_result.final_output)
    print(run_result.last_agent.name)


if __name__ == "__main__":
    asyncio.run(main())
