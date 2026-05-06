"""
What this file does:
Runs the A2A weather agent server and publishes its agent card directly from
the service endpoint.

In simple terms:
- this file starts the weather agent as a web server
- this file publishes the public A2A agent card for discovery
- this file registers that card in the central workshop registry
- this file connects incoming JSON-RPC A2A requests to the weather executor

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai
- Connected agent adapted from: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/__main__.py

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/agents/a2a/weather_agent/weather_server.py

Important sections:
- Step 1: Define the agent skill metadata
- Step 2: Build the public agent card
- Step 3: Register the card in the central registry
- Step 4: Configure the request handler and server
- Step 5: Start the server
"""

import asyncio
import uvicorn
import httpx
from google.protobuf.json_format import MessageToDict

from starlette.applications import Starlette
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
from agent_executor import WeatherAgentExecutor

AGENT_URL = "http://localhost:9999/"
REGISTRY_URL = "http://localhost:9990"


# ============================================================================
# STEP 1: SERVER ENTRY POINT
# ============================================================================
# This module is usually run directly. It defines the public metadata for the
# weather agent, wires the A2A request handler, and starts the Starlette app.

async def register_with_registry(public_agent_card: AgentCard) -> None:
    """Register the public card so the host can discover this agent dynamically."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{REGISTRY_URL}/registry/register",
                json=MessageToDict(public_agent_card),
            )
            response.raise_for_status()
        print("Weather agent registered with the central registry.")
    except Exception as exc:
        print(f"Weather agent could not register with the registry: {exc}")

if __name__ == '__main__':
    # =========================================================================
    # STEP 2: PUBLIC AGENT SKILL
    # =========================================================================
    # The skill tells other agents what this specialist can do.
    skill = AgentSkill(
        id='get_weather',
        name='get_weather',
        description='Provide weather details for a city or zipcode',
        tags=['weather'],
        examples=['get Chicago Weather'],
    )

    # =========================================================================
    # STEP 3: PUBLIC AGENT CARD
    # =========================================================================
    # The agent card is the document discovered by the host agent at the
    # well-known A2A route.
    public_agent_card = AgentCard(
        name="weather_agent",
        description='Provide weather details for the supplied location',
        version='1.0.0',
        default_input_modes=['text/plain'],
        default_output_modes=['text/plain'],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(
                protocol_binding='JSONRPC',
                url=AGENT_URL
            )
        ],
        skills=[skill],
    )

    # =========================================================================
    # STEP 4: REGISTRY REGISTRATION
    # =========================================================================
    asyncio.run(register_with_registry(public_agent_card))

    # =========================================================================
    # STEP 5: REQUEST HANDLER AND ROUTES
    # =========================================================================
    # These pieces connect incoming HTTP/A2A requests to the executor logic.
    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=public_agent_card,
        # extended_agent_card=extended_agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(public_agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, '/'))
    app = Starlette(routes=routes)

    # =========================================================================
    # STEP 6: START SERVER
    # =========================================================================
    print(f"Weather agent server is starting at {AGENT_URL}")
    uvicorn.run(app, host='0.0.0.0', port=9999)
