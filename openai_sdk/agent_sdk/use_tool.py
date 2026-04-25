""" What this file does:
Demonstrates function tools in the Agents SDK.
The agent can call a Python function when it helps answer the user prompt.

Documentation for reference:
- OpenAI Agents SDK Tools: https://developers.openai.com/api/docs/guides/tools
- Function calling guide: https://developers.openai.com/api/docs/guides/function-calling
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
uv run python -m openai_sdk.agent_sdk.use_tool

Safe experiments:
1. Add a second tool and update instructions for tool selection.
2. Try prompts that do and do not require tool usage.
3. Change tool return text and observe final output.

Important sections:
1. Step 1: Define a function tool.
2. Step 2: Build an agent with the tool attached.
3. Step 3: Run the agent and inspect the answer. """

import asyncio

from agents import Agent, Runner, function_tool
from openai_sdk.openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Tell me something surprising about ancient life on Earth."


@function_tool
def get_history_fun_fact() -> str:
    # Step 1: A simple tool the model may call.
    return "Sharks are older than trees."


def build_history_tutor_agent() -> Agent:
    # Step 2: Create an agent that knows when to use this tool.
    return Agent(
        name="History tutor",
        instructions="Answer history questions clearly. Use get_history_fun_fact when it helps.",
        model=MODEL_ID,
        tools=[get_history_fun_fact],
    )


async def main() -> None:
    # Step 3: Configure the OpenAI Agents SDK with OCI settings.
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 4: Run the agent. It can call the registered tool if useful.
    history_tutor = build_history_tutor_agent()
    run_result = await Runner.run(history_tutor, USER_PROMPT)

    # Step 5: Print the final answer.
    print("Final response:")
    print(run_result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
