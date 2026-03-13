# A2A (Agent-to-Agent) Communication System

## Overview

This folder contains a complete A2A (agent-to-agent) example built with OCI Generative AI, LangGraph, and multiple specialized services. The system demonstrates how a central orchestrator can discover remote agents, decide which one to call, and combine their outputs into a final response.

This part of the workshop is intentionally script-driven rather than notebook-driven because it depends on multiple long-running services that are easier to run in separate terminals.

## What This Module Demonstrates

This A2A example includes:

- **Agent Registry**: A shared discovery service for available agents
- **Specialized Agents**: City, clothes, and weather services with focused responsibilities
- **Main Orchestrator**: A LangGraph-based host agent that routes requests to specialists
- **Client Caching**: Reuse of A2A clients for better performance
- **Async Communication**: Non-blocking calls across remote agent services

## System Roles

The A2A workflow is split across four main responsibilities:

1. **Registry**
   - Keeps track of available agent cards
   - Allows the orchestrator to discover running services dynamically

2. **Specialized Agents**
   - `city_agent/`: Structured-output city recommendations
   - `clothes_agent/`: Tool-based clothing recommendations
   - `weather_agent/`: Tool-based weather responses

3. **Remote Connection Layer**
   - `remote_agent_connections.py` manages shared HTTP clients and cached A2A clients

4. **Main Orchestrator**
   - `langgraph_a2a_agent.py` builds a LangGraph workflow that delegates tasks to the best specialist

## Environment Setup

- `sandbox.yaml`: Contains OCI configuration and workshop settings.
- `.env`: Loads environment variables if required.
- All agents use OCI Generative AI models through the shared helper utilities.

## Files in This Folder

### Core Infrastructure

- `agent_registry.py`
  - In-memory registry service for agent discovery
  - Exposes registration, listing, and health endpoints
  - Runs on port `9990`

- `remote_agent_connections.py`
  - Shared A2A client and timeout management
  - Registry lookup and cached client creation
  - Used by the main orchestrator when calling remote agents

### Specialized Agent Folders

- `city_agent/`
  - Structured-output city recommendation service
  - Runs on port `9997`

- `clothes_agent/`
  - Tool-based clothing recommendation service
  - Runs on port `9998`

- `weather_agent/`
  - Tool-based weather service
  - Runs on port `9999`

### Main Orchestrator

- `langgraph_a2a_agent.py`
  - Discovers available agents from the registry
  - Builds a LangGraph workflow for A2A tool calls
  - Routes user requests to the correct specialists

## Architecture Overview

```text
User Query
   │
   ▼
langgraph_a2a_agent.py
   │
   ├── fetches available agents from agent_registry.py
   ├── builds a system prompt from discovered agent metadata
   └── calls one or more specialized agents through remote_agent_connections.py
           │
           ├── city_agent/
           ├── clothes_agent/
           └── weather_agent/
```

## How to Run the Full System

### 1. Start the registry

```bash
uv run langChain/agents/a2a/agent_registry.py
```

### 2. Start the specialized agents

Run each in a separate terminal:

```bash
uv run langChain/agents/a2a/city_agent/city_server.py
uv run langChain/agents/a2a/clothes_agent/clothes_server.py
uv run langChain/agents/a2a/weather_agent/weather_server.py
```

### 3. Start the main orchestrator

```bash
uv run langChain/agents/a2a/langgraph_a2a_agent.py
```

## Testing Individual Components

Each specialist agent includes a local test client:

```bash
uv run langChain/agents/a2a/city_agent/test_client.py
uv run langChain/agents/a2a/clothes_agent/test_client.py
uv run langChain/agents/a2a/weather_agent/test_client.py
```

## Example Queries

The orchestrator can handle multi-step queries such as:

- "What clothes should I wear on a trip to Oracle headquarters next week?"
- "Recommend a city for a tech conference and check the weather there"
- "What's the weather like and what should I wear in Chicago?"

## Key Concepts Demonstrated

- **Registry-Based Discovery**: Dynamic lookup of available agents
- **Specialized Services**: Different agent implementations for different tasks
- **Structured Output vs Tools**: Comparison of two agent design styles
- **Async Orchestration**: Remote calls inside a LangGraph workflow
- **Client Caching**: Connection reuse for better performance
- **A2A Protocol**: Standardized communication between agents

## API Endpoints

### Registry (`agent_registry.py` on port `9990`)

- `GET /registry/agents`: List all registered agents
- `POST /registry/register`: Register a new agent card
- `GET /health`: Registry health check

### Specialized Agents (`9997`-`9999`)

- `GET /.well-known/agent.json`: Agent card discovery
- `POST /message`: A2A message processing

## Troubleshooting

- **The orchestrator cannot find any agents**
  - Start the registry first, then restart the specialist agents so they can register themselves.

- **One of the ports is already in use**
  - Check ports `9990`, `9997`, `9998`, and `9999` for conflicts.

- **An agent does not appear in the registry**
  - Verify that the agent server started successfully and that it can reach `http://localhost:9990`.

- **Responses seem too simple or inconsistent**
  - These are workshop examples; the underlying tools and prompts are intentionally lightweight and can be expanded.

## Suggested Study Order

For the clearest learning path, review the files in this order:

1. `agent_registry.py`
2. `remote_agent_connections.py`
3. `city_agent/`
4. `clothes_agent/`
5. `weather_agent/`
6. `langgraph_a2a_agent.py`

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)
- [Structured Output](https://python.langchain.com/docs/how_to/structured_output/)

## Slack Channels

- **#generative-ai-users**: OCI Generative AI questions
- **#igiu-innovation-lab**: General project discussions
- **#igiu-ai-learning**: Help with environment setup and workshop examples

## Development Notes

- Agents register with the registry at startup.
- The orchestrator builds its understanding of the system from live registry data.
- Remote calls are cached to reduce repeated setup overhead.
- The examples are designed for learning and extension rather than production deployment.
