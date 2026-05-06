"""
What this file does:
Runs the A2A clothes agent server and publishes its agent card directly from
the service endpoint.

In simple terms:
- this file starts the clothes specialist as a web server
- this file exposes the public A2A card used by the host agent for discovery
- this file registers that card in the central workshop registry
- this file connects incoming A2A requests to the clothes executor

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
uv run langChain/agents/a2a/clothes_agent/clothes_server.py

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
from agent_executor import ClothesAgentExecutor

AGENT_URL = "http://localhost:9998/"
REGISTRY_URL = "http://localhost:9990"


# ============================================================================
# STEP 1: SERVER ENTRY POINT
# ============================================================================
# This module is usually run directly. It publishes the clothes agent metadata,
# creates the request routes, and starts the Starlette app.

async def register_with_registry(public_agent_card: AgentCard) -> None:
    """Register the public card so the host can discover this agent dynamically."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{REGISTRY_URL}/registry/register",
                json=MessageToDict(public_agent_card),
            )
            response.raise_for_status()
        print("Clothes agent registered with the central registry.")
    except Exception as exc:
        print(f"Clothes agent could not register with the registry: {exc}")

if __name__ == '__main__':
    # =========================================================================
    # STEP 2: PUBLIC AGENT SKILL
    # =========================================================================
    skill = AgentSkill(
        id='get_clothes',
        name='get_clothes',
        description='Recommend suitable clothing and accessories',
        tags=['clothes'],
        examples=['get clothes for male, rain weather'],
    )

    # =========================================================================
    # STEP 3: PUBLIC AGENT CARD
    # =========================================================================
    public_agent_card = AgentCard(
        name="clothes_agent",
        description='Recommend suitable clothing for the supplied conditions',
        version='1.0.0',
        default_input_modes=['text/plain'],
        default_output_modes=['text/plain'],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(
                protocol_binding='JSONRPC',
                url=AGENT_URL,
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
    request_handler = DefaultRequestHandler(
        agent_executor=ClothesAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=public_agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(public_agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, '/'))
    app = Starlette(routes=routes)

    # =========================================================================
    # STEP 6: START SERVER
    # =========================================================================
    print(f"Clothes agent server is starting at {AGENT_URL}")
    uvicorn.run(app, host='0.0.0.0', port=9998)
