"""
What this file does:
Runs the A2A city agent server, publishes its agent card, and registers the
service with the central registry.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/agents/a2a/city_agent/city_server.py

Important sections:
- Step 1: Define the agent skill metadata
- Step 2: Build the public agent card
- Step 3: Register with the central registry
- Step 4: Configure the request handler and server
- Step 5: Start the server
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
from agent_executor import CityAgentExecutor

# Constants
REGISTRY_URL = "http://localhost:9990"
AGENT_URL = "http://localhost:9997/"

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
        id='get_city',
        name='get_city',
        description='Recommend a city based on user criteria',
        tags=['place','city'],
        examples=['city where Oracle started'],
    )

    # Step 2: Create public agent card
    public_agent_card = AgentCard(
        name="city_agent",
        url=AGENT_URL,
        skills=[skill],
        default_input_modes=['text'],
        default_output_modes=['text'],
        description='Recommend a city based on the supplied criteria',
        version='1.0.0',
        capabilities=AgentCapabilities(streaming=True),
    )

    # Step 3: Register with central registry
    asyncio.run(register_with_registry(public_agent_card))

    # Step 4: Set up request handler and server
    request_handler = DefaultRequestHandler(
        agent_executor=CityAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    # Step 5: Start server
    uvicorn.run(server.build(), host='0.0.0.0', port=9997)
