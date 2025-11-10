from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import (
    AgentCard,
    TransportProtocol,
    Message,
    Role,
    Part,
    TextPart
)
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f"A2A_CALLS.{__name__}")

# All availble agent servers
remote_addresses = {
        'weather_agent':'http://localhost:9999/',
        'clothes_agent':'http://localhost:9998/',
        'city_agent':'http://localhost:9997/',
    }

# this function uses the url and agent name to fetch the response from the agent
async def call_a2a_agent(agent_name:str,message:str)->str:
    print("\n\nCalling the agent")
    print(agent_name)
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    EXTENDED_AGENT_CARD_PATH = '/agent/authenticatedExtendedCard'

    logger.debug("\na2a call function ===================")
    logger.debug(remote_addresses.keys())

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
            parts=[Part(root=TextPart(text=message))],
            message_id=str(uuid4())
        )

        ans = []
        async for chunk in client.send_message(request_message):
            if isinstance(chunk,Message):
                print(chunk.parts[-1].root.text) #type: ignore
                ans.extend(str(chunk.parts[-1].root.text))#type: ignore

        
        return str(ans)