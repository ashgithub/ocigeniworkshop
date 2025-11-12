from uuid import uuid4
from typing import Any
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig, ClientCallContext, A2AClient
from a2a.types import (
    AgentCard,
    TransportProtocol,
    Message,
    Role,
    Part,
    TextPart,
    SendMessageRequest,
    MessageSendParams
)
import logging

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f"A2A_CALLS.{__name__}")

# All availble agent servers
remote_addresses = {
        'weather_agent':'http://localhost:9999/',
        'clothes_agent':'http://localhost:9998/',
        'city_agent':'http://localhost:9997/',
    }

# this function uses the url and agent name to fetch the response from the agent
async def call_a2a_agent(agent_name:str,message:str)->str:
    print("\n\nCalling the agent via A2A:")
    print(agent_name)
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    EXTENDED_AGENT_CARD_PATH = '/agent/authenticatedExtendedCard'

    logger.debug("\na2a call function ===================")

    try:
        if agent_name not in remote_addresses.keys():
            return f"Wrong agent name, agent names are: {remote_addresses.keys()}"
    except Exception as e:
        logger.debug(e)
    
    base_url = remote_addresses[agent_name]

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        final_agent_card_to_use: AgentCard | None = None

        try:
            _public_card = (await resolver.get_agent_card())
            final_agent_card_to_use = _public_card
            logger.info('\nUsing PUBLIC agent card for client initialization (default).')

            if _public_card.supports_authenticated_extended_card:
                try:
                    auth_headers_dict = {
                        'Authorization': 'Bearer dummy-token-for-extended-card'
                    }
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={'headers': auth_headers_dict},
                    )
                    final_agent_card_to_use = (_extended_card)
                    logger.info('\nUsing AUTHENTICATED EXTENDED agent card for client')
                except Exception as e_extended:
                    logger.warning(
                        f'Failed to fetch extended agent card: {e_extended}. '
                        'Will proceed with public card.',
                        exc_info=True,
                    )
            elif (_public_card):
                logger.info('\nPublic card does not indicate support for an extended card. Using public card.')

        except Exception as e:
            logger.error(f'Critical error fetching public agent card: {e}', exc_info=True)
            raise RuntimeError('Failed to fetch the public agent card. Cannot continue.') from e

        # config = ClientConfig(
        #     httpx_client=httpx_client,
        #     supported_transports=[
        #         TransportProtocol.http_json,
        #         TransportProtocol.jsonrpc
        #     ]
        # )
        # factory = ClientFactory(config)
        # client = factory.create(final_agent_card_to_use)

        # request_message = Message(
        #     role=Role.user,
        #     parts=[Part(root=TextPart(text=message))],
        #     message_id=str(uuid4())
        # )

        # ans = []
        # try:
        #     async for chunk in client.send_message(request_message, request_metadata={'timeout':300}):
        #         if isinstance(chunk,Message):
        #             print(chunk.parts[-1].root.text) #type: ignore
        #             ans.extend(str(chunk.parts[-1].root.text))#type: ignore
        # except Exception as e:
        #     print("Error in streaming response")
        #     print(e)

        client = A2AClient(httpx_client=httpx_client, agent_card=final_agent_card_to_use)
        logger.info('A2AClient initialized.')
        timeout = 50.0

        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': message}
                ],
                'message_id': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        print("Starting A2A response stream...\n")
        try:
            response = await client.send_message(request, http_kwargs={"timeout": timeout})
            ans = response.model_dump(mode='json', exclude_none=True)
            print("A2A response:")
            print(ans)
        except Exception as e:
            ans = f"Error in response: {e}"
                
        return str(ans)
    
async def test():
    response = await call_a2a_agent("city_agent","What is the city where are most piramids?")

    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())