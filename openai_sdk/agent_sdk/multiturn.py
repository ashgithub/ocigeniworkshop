""" What this file does:
Demonstrates two multi-turn memory patterns:
1) local conversation memory using `SQLiteSession`
2) server-linked memory using `previous_response_id`

Documentation for reference:
- OpenAI Agents SDK Running agents: https://developers.openai.com/api/docs/guides/agents/running-agents
- OpenAI Agents guide: https://developers.openai.com/api/docs/guides/agents/quickstart
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
uv run openai_sdk/agent_sdk/multiturn.py

Safe experiments:
1. Change `SESSION_ID` and compare local memory behavior.
2. Add a third turn and inspect whether context is preserved.
3. Try different concise-vs-detailed instructions for the same turns.

Important sections:
1. Step 1: Build one reusable tour-guide agent.
2. Step 2: Run local memory turns with `SQLiteSession`.
3. Step 3: Run server-linked turns with `previous_response_id`. """

import asyncio

from agents import Agent, Runner, SQLiteSession
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
SESSION_ID = "conversation_123"

def build_tour_guide_agent() -> Agent:
    # Step 1: Create one agent reused in both multi-turn patterns.
    return Agent(
        name="Tour guide",
        instructions="Answer with compact travel facts. Reply concisely",
        model=MODEL_ID,
    )

async def main() -> None:
    # Step 2: Configure the OpenAI Agents SDK with OCI settings.
    OpenAIClientProvider().configure_agents_oci_env()

    # Step 3: Build shared objects used in the examples.
    tour_guide = build_tour_guide_agent()
    session = SQLiteSession(SESSION_ID)

    # Step 4: Run a local multi-turn conversation with SQLite session memory.
    local_first_turn = await Runner.run(
        tour_guide,
        "What city is the Golden Gate Bridge in?",
        session=session,
    )
    print("Local turn 1:")
    print(local_first_turn.final_output)

    local_second_turn = await Runner.run(
        tour_guide,
        "Tell me another interesting fact about that city",
        session=session,
    )
    print("Local turn 2:")
    print(local_second_turn.final_output)

    # Step 5: Run server-linked turns using previous_response_id.
    server_first_turn = await Runner.run(
        tour_guide,
        "Where is located the statue of liberty?",
    )
    print("Server turn 1:")
    print(server_first_turn.final_output)

    server_second_turn = await Runner.run(
        tour_guide,
        "So, when was it placed?",
        previous_response_id=server_first_turn.last_response_id,
    )
    print("Server turn 2:")
    print(server_second_turn.final_output)

if __name__ == "__main__":
    asyncio.run(main())
