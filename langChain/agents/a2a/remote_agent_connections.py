"""
What this file does:
Provides cached A2A client connections for the main orchestrator so it can call
specialized agents efficiently.

Documentation to reference:
- A2A protocol: https://a2a-protocol.org/latest/topics/key-concepts/, https://a2a-protocol.org/latest/tutorials/python/1-introduction/#tutorial-sections
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- OCI OpenAI compatible SDK: https://github.com/oracle-samples/oci-openai

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI configuration and workshop settings.
- .env: Loads environment variables if required.

How to run the file:
This file is not run directly. It is imported by `langgraph_a2a_agent.py`.

Important sections:
- Step 1: Imports and shared configuration
- Step 2: Shared HTTP client lifecycle management
- Step 3: Cached client lookup and registry-based client creation
- Step 4: A2A message sending
- Step 5: Cleanup and local test helper

Registry URL: http://localhost:9990
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict

import httpx
from a2a.client import (
    Client,
    ClientConfig,
    ClientFactory,
)
from a2a.types import TransportProtocol, AgentCard

# Step 1: Imports and shared configuration
# Configure global timeout behavior for shared A2A HTTP calls.
GLOBAL_TIMEOUT = httpx.Timeout(
    timeout=30.0,
    connect=5.0,
    read=25.0,
    write=5.0,
)

# Registry endpoint used for dynamic agent discovery.
REGISTRY_URL = "http://localhost:9990"

# Shared HTTP client used across cached A2A clients.
_shared_httpx_client: Optional[httpx.AsyncClient] = None

# Cache A2A client objects to avoid repeated creation.
_client_cache: Dict[str, Client] = {}

# Step 2: Shared HTTP client lifecycle management
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

# Step 3: Cached client lookup and registry-based client creation
async def _get_cached_client(agent_name: str) -> Optional[Client]:
    """Get cached client or create new one from registry."""
    # Step 3.1: Return the cached client when available.
    if agent_name in _client_cache:
        return _client_cache[agent_name]

    # Step 3.2: Query the registry and build a client for the matching agent.
    try:
        async with _get_shared_httpx_client() as httpx_client:
            response = await httpx_client.get(f"{REGISTRY_URL}/registry/agents")
            response.raise_for_status()
            agents = response.json()

            # Step 3.3: Find the agent card by name and create the A2A client.
            for agent_data in agents:
                if agent_data.get('name') == agent_name:
                    agent_card = AgentCard(**agent_data)

                    config = ClientConfig(
                        httpx_client=httpx_client,
                        supported_transports=[
                            TransportProtocol.jsonrpc,
                            TransportProtocol.http_json,
                        ],
                        streaming=agent_card.capabilities.streaming or False,
                    )
                    client = ClientFactory(config).create(agent_card)

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
    # Step 4: A2A message sending
    try:
        # Step 4.1: Retrieve or create the cached client for the requested agent.
        client = await _get_cached_client(agent_name)
        if not client:
            return f"Agent '{agent_name}' not found in registry"

        from a2a.client import create_text_message_object

        # Step 4.2: Build the request payload.
        request = create_text_message_object(content=message)

        # Step 4.3: Stream the response and collect all parts.
        response_parts = []
        async for response in client.send_message(request):
            response_parts.append(str(response))

        return " ".join(response_parts) if response_parts else "No response received"

    except Exception as e:
        _client_cache.pop(agent_name, None)
        return f"Error calling {agent_name}: {str(e)}"

# Step 5: Cleanup and local test helper
async def cleanup_clients():
    """Cleanup cached clients and shared httpx client."""
    # Step 5.1: Clear cached clients and close the shared HTTP client.
    global _shared_httpx_client
    _client_cache.clear()
    if _shared_httpx_client:
        await _shared_httpx_client.aclose()
        _shared_httpx_client = None

async def test():
    """Test function for development."""
    # Step 5.2: Run a simple local connectivity test.
    response = await call_a2a_agent("city_agent", "What is the city where are most pyramids?")
    print(response)

if __name__ == "__main__":
    asyncio.run(test())
