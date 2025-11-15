"""
What this file does:
Main A2A server for the clothes agent that provides clothing recommendation functionality and handles agent discovery

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai  note: supports OpenAI, XAI & Meta models. Also supports OpenAI Responses API

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI
 - #igiu-innovation-lab: general discussions on your project
 - #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/agents/a2a/clothes_agent/clothes_server.py

Comments to important sections of file:
- Step 1: Define agent skill
- Step 2: Create public agent card
- Step 3: Register with central registry
- Step 4: Set up request handler and server
- Step 5: Start server
"""

import asyncio
import uvicorn
import httpx

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import ClothesAgentExecutor

# Constants
REGISTRY_URL = "http://localhost:9990"
AGENT_URL = "http://localhost:9998/"

async def register_with_registry(agent_card: AgentCard):
    """Register the agent with the central registry at startup."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{REGISTRY_URL}/registry/register",
                json=agent_card.model_dump()
            )
            if response.status_code == 201:
                print(f"Successfully registered {agent_card.name} with registry")
            else:
                print(f"Failed to register {agent_card.name}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error registering {agent_card.name} with registry: {e}")

if __name__ == '__main__':
    # Step 1: Define agent skill
    skill = AgentSkill(
        id='get_clothes',
        name='get_clothes',
        description='Gets the best clothes to wear',
        tags=['clothes'],
        examples=['get clothes for male, rain weather'],
    )

    # Step 2: Create public agent card
    public_agent_card = AgentCard(
        name="clothes_agent",
        url=AGENT_URL,
        skills=[skill],
        default_input_modes=['text'],
        default_output_modes=['text'],
        description='Gets the suitable clothes for the time',
        version='1.0.0',
        capabilities=AgentCapabilities(streaming=True),
    )

    # Step 3: Register with central registry
    asyncio.run(register_with_registry(public_agent_card))

    # Step 4: Set up request handler and server
    request_handler = DefaultRequestHandler(
        agent_executor=ClothesAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    # Step 5: Start server
    uvicorn.run(server.build(), host='0.0.0.0', port=9998)
