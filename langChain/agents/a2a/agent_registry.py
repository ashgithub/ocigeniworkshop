"""
What this file does:
Provides a simple in-memory A2A agent registry server. Agents register at
startup so the main orchestrator can discover them dynamically.

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
- Step 1: Registry storage using an in-memory dictionary for agent cards
- Step 2: API endpoints for register, list, health check, and get-by-URL
- Step 3: Server startup on port 9990 for A2A agent registration
"""


from typing import List, Optional, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from a2a.types import AgentCard

# Step 1: Simple in-memory registry using a dictionary
agents: Dict[str, AgentCard] = {}

# Step 2: Create the FastAPI application and endpoints
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
    # Step 3: Start the registry server
    uvicorn.run(app, host="0.0.0.0", port=9990)
