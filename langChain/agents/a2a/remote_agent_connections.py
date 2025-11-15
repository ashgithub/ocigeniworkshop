"""
What this file does:
Provides optimized A2A (Agent-to-Agent) communication functionality for the main agent to call specialized agents. Uses client caching for maximum performance with global timeout configuration.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai  note: supports OpenAI, XAI & Meta models. Also supports OpenAI Responses API

Relevant slack channels:
 - #generative-ai-users: for questions on OCI Gen AI
 - #igiu-innovation-lab: general discussions on your project
 - #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, DB details, and wallet path.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
This file is not run directly, but imported by main.py for A2A agent communication.

Comments to important sections of file:
- Step 1: Global configuration and client caching setup
- Step 2: Registry integration for dynamic agent discovery
- Step 3: Optimized A2A client creation and caching
- Step 4: Streamlined message sending with cached clients

Registry URL: http://localhost:9990
"""

import httpx
import asyncio
from a2a.client import (
    Client,
    ClientConfig,
    ClientFactory,
)
from a2a.types import TransportProtocol, AgentCard
from a2a.utils.message import get_message_text
from typing import Optional, Dict
from contextlib import asynccontextmanager

# Global timeout configuration
GLOBAL_TIMEOUT = httpx.Timeout(
    timeout=30.0,    # total timeout
    connect=5.0,     # connection timeout
    read=25.0,       # read timeout
    write=5.0        # write timeout
)

# Registry configuration
REGISTRY_URL = "http://localhost:9990"

# Global httpx client for all cached A2A clients
_shared_httpx_client: Optional[httpx.AsyncClient] = None

# Cache for client objects to avoid repeated creation
_client_cache: Dict[str, Client] = {}

@asynccontextmanager
async def _get_shared_httpx_client():
    """Get or create the shared httpx client."""
    global _shared_httpx_client
    if _shared_httpx_client is None:
        _shared_httpx_client = httpx.AsyncClient(timeout=GLOBAL_TIMEOUT)
    try:
        yield _shared_httpx_client
    except Exception:
        # If client fails, reset it for next use
        if _shared_httpx_client:
            await _shared_httpx_client.aclose()
        _shared_httpx_client = None
        raise

async def _get_cached_client(agent_name: str) -> Optional[Client]:
    """Get cached client or create new one from registry."""
    # Check cache first
    if agent_name in _client_cache:
        return _client_cache[agent_name]

    # Fetch agent card from registry
    try:
        async with _get_shared_httpx_client() as httpx_client:
            response = await httpx_client.get(f"{REGISTRY_URL}/registry/agents")
            response.raise_for_status()
            agents = response.json()

            # Find agent by name and create client
            for agent_data in agents:
                if agent_data.get('name') == agent_name:
                    agent_card = AgentCard(**agent_data)

                    # Create A2A client
                    config = ClientConfig(
                        httpx_client=httpx_client,
                        supported_transports=[
                            TransportProtocol.jsonrpc,
                            TransportProtocol.http_json,
                        ],
                        streaming=agent_card.capabilities.streaming or False,
                    )
                    client = ClientFactory(config).create(agent_card)

                    # Cache the client
                    _client_cache[agent_name] = client
                    return client

            return None
    except Exception:
        return None

async def call_a2a_agent(agent_name: str, message: str) -> str:
    """
    High-performance A2A agent call using client caching and global timeout configuration.

    Args:
        agent_name: Name of the agent to call (city_agent, clothes_agent, weather_agent)
        message: The message/query to send to the agent

    Returns:
        str: Agent response or error message
    """
    try:
        # Step 1: Get cached client (creates if needed)
        client = await _get_cached_client(agent_name)
        if not client:
            return f"Agent '{agent_name}' not found in registry"

        # Step 2: Send message using cached client (maximum performance)
        from a2a.client import create_text_message_object
        request = create_text_message_object(content=message)

        # Collect all response parts (simple approach like test client)
        response_parts = []
        async for response in client.send_message(request):
            response_parts.append(str(response))

        return " ".join(response_parts) if response_parts else "No response received"

    except Exception as e:
        # Clear failed client from cache to force recreation on next call
        _client_cache.pop(agent_name, None)
        return f"Error calling {agent_name}: {str(e)}"

async def cleanup_clients():
    """Cleanup cached clients and shared httpx client."""
    global _shared_httpx_client
    _client_cache.clear()
    if _shared_httpx_client:
        await _shared_httpx_client.aclose()
        _shared_httpx_client = None

async def test():
    """Test function for development."""
    response = await call_a2a_agent("city_agent", "What is the city where are most pyramids?")
    print(response)

if __name__ == "__main__":
    asyncio.run(test())
