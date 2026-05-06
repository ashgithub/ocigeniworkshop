"""
What this file does:
Provides a small in-memory registry for A2A agent cards so the host agent can
discover specialist agents dynamically.

In simple terms:
- specialist servers send their public agent card here when they start
- the host agent asks this registry which agents are available
- the registry returns the latest list of registered cards

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
uv run langChain/agents/a2a/agent_registry.py

Sample commands:
- http localhost:9990/registry/agents
- http localhost:9990/health

Important sections:
- Step 1: Store registered agent cards in memory
- Step 2: Accept new registrations from specialist servers
- Step 3: Return the current list of registered agents
- Step 4: Start the FastAPI registry server
"""

from __future__ import annotations

from google.protobuf.json_format import MessageToDict, ParseDict
from fastapi import FastAPI, HTTPException
import uvicorn

from a2a.types import AgentCard


# ============================================================================
# STEP 1: IN-MEMORY REGISTRY STORAGE
# ============================================================================
# This workshop registry intentionally keeps things simple: cards are stored in
# memory and are keyed by agent name. Restarting the registry clears the list.

agents_by_name: dict[str, AgentCard] = {}

app = FastAPI(
    title="A2A Agent Registry Server",
    description="Simple FastAPI server for dynamic A2A agent discovery.",
)


def _card_to_dict(agent_card: AgentCard) -> dict:
    """Convert a protobuf AgentCard into a JSON-ready dictionary."""
    return MessageToDict(agent_card)


def _card_lookup_key(agent_card: AgentCard) -> str:
    """Choose a stable registry key for this agent card."""
    return agent_card.name or (
        agent_card.supported_interfaces[0].url
        if agent_card.supported_interfaces
        else "unknown-agent"
    )


# ============================================================================
# STEP 2: REGISTRATION ENDPOINTS
# ============================================================================
# Specialist servers call these endpoints during startup so the host can later
# discover them without hard-coding every agent URL.

@app.post("/registry/register", status_code=201)
async def register_agent(agent_card_data: dict):
    """Register or update one agent card in the registry."""
    agent_card = ParseDict(agent_card_data, AgentCard())
    key = _card_lookup_key(agent_card)
    agents_by_name[key] = agent_card

    print(f"Registry stored agent '{key}'.")
    return _card_to_dict(agent_card)


@app.get("/registry/agents")
async def list_registered_agents():
    """List all currently registered agent cards."""
    return [_card_to_dict(agent_card) for agent_card in agents_by_name.values()]


@app.get("/registry/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get one registered agent card by name."""
    agent_card = agents_by_name.get(agent_name)
    if agent_card is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found in registry.",
        )
    return _card_to_dict(agent_card)


@app.get("/health")
async def health_check():
    """Basic health endpoint for local workshop testing."""
    return {
        "status": "healthy",
        "registered_agents": len(agents_by_name),
    }


# ============================================================================
# STEP 4: SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("Agent registry server is starting at http://localhost:9990")
    uvicorn.run(app, host="0.0.0.0", port=9990)
