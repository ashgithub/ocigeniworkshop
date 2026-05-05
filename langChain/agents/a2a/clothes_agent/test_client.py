"""
What this file does:
Provides a simple test client for the clothes A2A agent.

In simple terms:
- this file checks whether the clothes server is reachable
- this file downloads the public agent card exposed by the server
- this file sends one sample request in non-streaming mode
- this file sends the same request in streaming mode when supported

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai
- Connected agent adapted from: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/__main__.py
- Test client adapted from: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/test_client.py

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
uv run langChain/agents/a2a/clothes_agent/test_client.py

Important sections:
- Step 1: Define the test server URL and sample request
- Step 2: Fetch and display the public agent card
- Step 3: Run a non-streaming test message
- Step 4: Run a streaming test message
"""

import asyncio

import httpx

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import (
    display_agent_card,
    get_stream_response_text,
    new_text_message,
)
from a2a.types.a2a_pb2 import Role, SendMessageRequest
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


# ============================================================================
# STEP 1: TEST SETTINGS
# ============================================================================

AGENT_NAME = "clothes_agent"
AGENT_BASE_URL = "http://127.0.0.1:9998"
TEST_QUERY = "What clothes should I wear if it is 55 F and raining?"


# ============================================================================
# STEP 2: AGENT CARD DISCOVERY
# ============================================================================

async def fetch_public_agent_card(httpx_client: httpx.AsyncClient):
    """Resolve and display the public card exposed by the clothes server."""
    resolver = A2ACardResolver(
        httpx_client=httpx_client,
        base_url=AGENT_BASE_URL,
    )

    print(
        f"Fetching {AGENT_NAME} card from "
        f"{AGENT_BASE_URL}{AGENT_CARD_WELL_KNOWN_PATH}"
    )
    public_card = await resolver.get_agent_card()
    display_agent_card(public_card)
    return public_card


# ============================================================================
# STEP 3: NON-STREAMING TEST
# ============================================================================

async def run_non_streaming_test(public_card) -> None:
    """Send one non-streaming request and print the final text response."""
    client = await create_client(
        agent=public_card,
        client_config=ClientConfig(streaming=False),
    )
    try:
        request = SendMessageRequest(
            message=new_text_message(TEST_QUERY, role=Role.ROLE_USER)
        )

        print(f"Testing {AGENT_NAME} in non-streaming mode with: {TEST_QUERY}")
        async for response in client.send_message(request):
            response_text = get_stream_response_text(response).strip()
            if response_text:
                print(f"Non-streaming response: {response_text}")
    finally:
        await client.close()


# ============================================================================
# STEP 4: STREAMING TEST
# ============================================================================

async def run_streaming_test(public_card) -> None:
    """Send one streaming request and print each text update received."""
    if not public_card.capabilities.streaming:
        print(f"{AGENT_NAME} does not advertise streaming support.")
        return

    client = await create_client(
        agent=public_card,
        client_config=ClientConfig(streaming=True),
    )
    try:
        request = SendMessageRequest(
            message=new_text_message(TEST_QUERY, role=Role.ROLE_USER)
        )

        print(f"Testing {AGENT_NAME} in streaming mode with: {TEST_QUERY}")
        async for response in client.send_message(request):
            response_text = get_stream_response_text(response).strip()
            if response_text:
                print(f"Streaming response: {response_text}")
    finally:
        await client.close()


async def main() -> None:
    """Run discovery plus both request styles against the clothes server."""
    timeout_config = httpx.Timeout(
        timeout=60.0,
        connect=5.0,
        read=50.0,
        write=5.0,
    )

    async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
        public_card = await fetch_public_agent_card(httpx_client)
        await run_non_streaming_test(public_card)
        await run_streaming_test(public_card)


if __name__ == '__main__':
    asyncio.run(main())
