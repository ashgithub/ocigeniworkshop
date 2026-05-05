"""
What this file does:
Provides a simple test client for the weather A2A agent.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- A2A samples: https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/travel_planner_agent

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/agents/a2a/weather_agent/test_client.py

This test client was adapted from:
https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/test_client.py
"""
import httpx

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import display_agent_card, new_text_message
from a2a.types.a2a_pb2 import (
    GetExtendedAgentCardRequest,
    Role,
    SendMessageRequest,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


async def main() -> None:
    # --8<-- [start:A2ACardResolver]
    base_url = 'http://127.0.0.1:9999'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default
        )

        # --8<-- [end:A2ACardResolver]

        print(
            f'Attempting to fetch public agent card from: {base_url}{AGENT_CARD_WELL_KNOWN_PATH}'
        )
        public_card = await resolver.get_agent_card()
        print('\nSuccessfully fetched public agent card:')
        display_agent_card(public_card)

        print('\n--- Non-Streaming Call ---')
        # --8<-- [start:message_send]
        config = ClientConfig(streaming=False)
        client = await create_client(agent=public_card, client_config=config)
        print('\nNon-streaming Client initialized.')

        message = new_text_message('Say hello.', role=Role.ROLE_USER)
        request = SendMessageRequest(message=message)

        print('Response:')
        async for chunk in client.send_message(request):
            print(chunk)
        # --8<-- [end:message_send]

        print('\n--- Streaming Call ---')
        # --8<-- [start:message_stream]
        streaming_config = ClientConfig(streaming=True)
        streaming_client = await create_client(
            agent=public_card, client_config=streaming_config
        )
        print('\nStreaming Client initialized.')

        streaming_response = streaming_client.send_message(request)

        async for chunk in streaming_response:
            print('Response chunk:')
            print(chunk)
        # --8<-- [end:message_stream]

        await streaming_client.close()

        print('\n--- Extended Card Call ---')
        extended_card = await client.get_extended_agent_card(
            GetExtendedAgentCardRequest()
        )
        print('\nSuccessfully fetched authenticated extended agent card:')
        display_agent_card(extended_card)

        await client.close()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
