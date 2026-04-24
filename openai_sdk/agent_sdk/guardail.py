""" What this file does:
Demonstrates an input guardrail that blocks math-homework requests.
A small classifier agent runs first; if it trips the guardrail, the main
support agent is not allowed to continue.

Documentation for reference:
- OpenAI SDK Input guardrails: https://developers.openai.com/api/docs/guides/agents/guardrails
- GenAI platform GA docs (VPN): https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

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
uv run python agent_sdk/guardail.py

Safe experiments:
1. Change `TEST_PROMPT` to a non-math request and compare behavior.
2. Update classifier instructions and observe false positives/negatives.
3. Add a second category flag to the schema.

Important sections:
1. Step 1: Define guardrail output schema.
2. Step 2: Build classifier guardrail agent.
3. Step 3: Attach guardrail to main support agent.
4. Step 4: Run and catch tripwire events. """

import asyncio

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from pydantic import BaseModel
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
TEST_PROMPT = "Can you solve 2x + 3 = 11 for me?"

# Step 1: Define classifier output type for the guardrail decision.
class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

# Step 2: Build a guardrail classifier agent.
guardrail_agent = Agent(
    name="Homework check",
    instructions="Detect whether the user is asking for math homework help.",
    output_type=MathHomeworkOutput,
    model=MODEL_ID,
)

# Step 3: Run the guardrail classifier before sending input to main agent.
@input_guardrail
async def math_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

# Step 4: Main agent for normal requests.
agent = Agent(
    name="Customer support",
    instructions="Help customers with support questions.",
    input_guardrails=[math_guardrail],
    model=MODEL_ID,
)

async def main() -> None:
    # Step 5: Configure environment for using OCI auth and not native OpenAI.
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 6: Run a prompt that may trigger the guardrail.
    try:
        await Runner.run(agent, TEST_PROMPT)
    except InputGuardrailTripwireTriggered:
        print("Guardrail blocked the request.")

if __name__ == "__main__":
    asyncio.run(main())
