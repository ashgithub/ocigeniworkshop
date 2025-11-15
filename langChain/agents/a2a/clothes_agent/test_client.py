"""
What this file does:
Sample test client for the clothes agent, demonstrating how to interact with the A2A agent using A2A client.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- A2A samples: https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/travel_planner_agent

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI
 - #igiu-innovation-lab: general discussions on your project
 - #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/agents/a2a/clothes_agent/test_client.py

This test client was adopted from https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/travel_planner_agent/loop_client.py
"""

import asyncio
import httpx

from a2a.client import (
    A2ACardResolver,
    Client,
    ClientConfig,
    ClientFactory,
    create_text_message_object,
)
from a2a.types import TransportProtocol
from a2a.utils.message import get_message_text


async def test_clothes_agent() -> None:
    """Send a test query to the clothes agent and print the response."""

    test_query = "What clothes should I wear for a rainy day?"

    timeout_config = httpx.Timeout(
        timeout=60.0,    # total timeout
        connect=5.0,     # connection timeout
        read=50.0,       # read timeout
        write=5.0        # write timeout
    )

    async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url='http://localhost:9998',
            # agent_card_path uses default, extended_agent_card_path also uses default
        )

        try:
            agent_card = await resolver.get_agent_card()

            # Create A2A client with the agent card
            config = ClientConfig(
                httpx_client=httpx_client,
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                streaming=agent_card.capabilities.streaming or False,
            )
            client = ClientFactory(config).create(agent_card)

            print(f"Sending test query: {test_query}")

            # Create the message object
            request = create_text_message_object(content=test_query)

            # Send the request and get the streaming messages
            async for response in client.send_message(request):
                print(f"Response: {response}")
                print("-------")
                print(get_message_text(response))

        except Exception as e:
            print(f'An error occurred: {e}')


async def main() -> None:
    await test_clothes_agent()


if __name__ == '__main__':
    asyncio.run(main())
