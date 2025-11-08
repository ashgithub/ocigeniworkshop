from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient, ClientFactory, ClientConfig
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
    TransportProtocol,
    Message,
    Role,
    Part,
    TextPart
)

async def main() -> None:
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    EXTENDED_AGENT_CARD_PATH = '/agent/authenticatedExtendedCard'

    # --8<-- [start:A2ACardResolver]

    base_url = 'http://localhost:9999'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default, extended_agent_card_path also uses default
        )
        # --8<-- [end:A2ACardResolver]

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:
            print(f'Attempting to fetch public agent card from: {base_url}{PUBLIC_AGENT_CARD_PATH}')
            _public_card = (await resolver.get_agent_card())  # Fetches from default public path
            print('Successfully fetched public agent card:')
            # print(_public_card.model_dump_json(indent=2, exclude_none=True))
            final_agent_card_to_use = _public_card
            print('\nUsing PUBLIC agent card for client initialization (default).')

            if _public_card.supports_authenticated_extended_card:
                try:
                    print(f'Public card supports authenticated extended card. Attempting to fetch from: {base_url}{EXTENDED_AGENT_CARD_PATH}')
                    auth_headers_dict = {'Authorization': 'Bearer dummy-token-for-extended-card'}
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={'headers': auth_headers_dict},
                    )
                    print('Successfully fetched authenticated extended agent card:')
                    # print(_extended_card.model_dump_json(indent=2, exclude_none=True))
                    final_agent_card_to_use = _extended_card
                    print('Using AUTHENTICATED EXTENDED agent card for client initialization.')
                except Exception as e_extended:
                    print(f'Failed to fetch extended agent card: {e_extended}. Will proceed with public card.')
            elif (_public_card):  # supportsAuthenticatedExtendedCard is False or None
                print('Public card does not indicate support for an extended card. Using public card.')

        except Exception as e:
            print(f'Critical error fetching public agent card: {e}')
            raise RuntimeError('Failed to fetch the public agent card. Cannot continue.') from e

        config = ClientConfig(
            httpx_client=httpx_client,
            supported_transports=[
                TransportProtocol.http_json,
                TransportProtocol.jsonrpc
            ]
        )
        factory = ClientFactory(config)
        client = factory.create(final_agent_card_to_use)

        request_message = Message(
            role=Role.user,
            parts=[Part(root=TextPart(text="Hello agent"))],
            message_id=str(uuid4())
        )

        async for chunk in client.send_message(request_message):
            if isinstance(chunk,Message):
                print(chunk.parts[-1].root.text) #type: ignore

if __name__ == '__main__':
    import asyncio

    asyncio.run(main())