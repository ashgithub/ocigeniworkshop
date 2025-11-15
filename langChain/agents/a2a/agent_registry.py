"""
What this file does:
Creates a simple in-memory AI Agents registry server using A2A protocol. Agents register themselves at startup for automatic discovery.

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
uv run langChain/agents/a2a/agent_registry.py

Sample commands:
- http localhost:9990/registry/agents
- http localhost:9990/health

Comments to important sections of file:
- Registry storage: Simple in-memory dict for agent cards
- Endpoints: Register, list agents, health check, get agent by URL
- Server startup: Runs on port 9990 for agent registration

- Agents that register themselves: city_agent, clothes_agent, weather_agent


"""


import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict
from a2a.types import AgentCard

# Simple in-memory registry using dict
agents: Dict[str, AgentCard] = {}

app = FastAPI(title="A2A Agent Registry Server", description="Simple FastAPI server for agent discovery")

@app.post("/registry/register", response_model=AgentCard, status_code=201)
async def register_agent(agent_card: AgentCard):
    """Registers a new agent with the registry."""
    print(f"Registering agent: {agent_card.name} at {agent_card.url}")
    agents[agent_card.url] = agent_card
    return agent_card

@app.get("/registry/agents", response_model=List[AgentCard])
async def list_registered_agents():
    """Lists all currently registered agents."""
    # list agent_names get hem from agent cards
    return list(agents.values())

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/registry/agents/{url}", response_model=AgentCard)
async def get_agent(url: str):
    """Get a specific agent by URL."""
    agent = agents.get(url)
    if agent:
        print(f"Returning agent: {agent.name}")
        return agent
    raise HTTPException(status_code=404, detail=f"Agent with URL '{url}' not found")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=9990)
