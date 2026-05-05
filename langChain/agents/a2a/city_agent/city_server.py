"""
What this file does:
Runs the A2A city agent server and publishes its agent card directly from the
service endpoint.

In simple terms:
- this file starts the city specialist as a web server
- this file exposes the public agent card used for direct discovery
- this file connects incoming A2A requests to the city executor

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
uv run langChain/agents/a2a/city_agent/city_server.py

Important sections:
- Step 1: Define the agent skill metadata
- Step 2: Build the public agent card
- Step 3: Configure the request handler and server
- Step 4: Start the server
"""

import uvicorn

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
from agent_executor import CityAgentExecutor

AGENT_URL = "http://localhost:9997/"


# ============================================================================
# STEP 1: SERVER ENTRY POINT
# ============================================================================
# This module is usually run directly. It defines the public metadata for the
# city agent, wires the A2A routes, and starts the Starlette application.

if __name__ == '__main__':
    # =========================================================================
    # STEP 2: PUBLIC AGENT SKILL
    # =========================================================================
    skill = AgentSkill(
        id='get_city',
        name='get_city',
        description='Recommend a city based on user criteria',
        tags=['place','city'],
        examples=['city where Oracle started'],
    )

    # =========================================================================
    # STEP 3: PUBLIC AGENT CARD
    # =========================================================================
    public_agent_card = AgentCard(
        name="city_agent",
        description='Recommend a city based on the supplied criteria',
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
    # STEP 4: REQUEST HANDLER AND ROUTES
    # =========================================================================
    request_handler = DefaultRequestHandler(
        agent_executor=CityAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=public_agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(public_agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, '/'))
    app = Starlette(routes=routes)

    # =========================================================================
    # STEP 5: START SERVER
    # =========================================================================
    print(f"City agent server is starting at {AGENT_URL}")
    uvicorn.run(app, host='0.0.0.0', port=9997)
