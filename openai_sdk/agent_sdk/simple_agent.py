""" What this file does:
Demonstrates the smallest end-to-end Agents SDK flow:
1) create one agent, 2) run one prompt, 3) print one answer.

Documentation for reference:
- OpenAI Agents SDK Quickstart: https://developers.openai.com/api/docs/guides/agents/quickstart
- OpenAI Agents SDK Overview: https://developers.openai.com/api/docs/guides/agents
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
uv run openai_sdk/agent_sdk/simple_agent.py

Safe experiments:
1. Change USER_PROMPT to ask another history question.
2. Replace MODEL_ID with another model available in your OCI project.
3. Adjust instructions to compare response style.

Important sections:
1. Step 1: Build one minimal agent.
2. Step 2: Configure OCI-backed SDK client and run one prompt.
3. Step 3: Print the final output. """

import asyncio

from agents import Agent, Runner
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "When did the Roman Empire fall?"

def build_history_tutor_agent() -> Agent:
    # Step 1: Create a minimal single-purpose agent.
    return Agent(
        name="History tutor",
        instructions="You answer history questions clearly and concisely.",
        model=MODEL_ID,
    )

async def main() -> None:
    # Step 2: Configure the OpenAI Agents SDK to use your OCI-backed client.
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 3: Build the agent and run one prompt.
    history_tutor = build_history_tutor_agent()
    run_result = await Runner.run(history_tutor, USER_PROMPT)

    # Step 4: Print the final model response.
    print("Final response:")
    print(run_result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
