# A2A (Agent-to-Agent) Communication System

This folder contains the workshop A2A example built around dynamic discovery.
Each specialist agent publishes its own A2A card and also registers that card
in a small local registry. The LangGraph host uses that registry to discover
which specialist agents are currently available.

## Main Pieces

- `agent_registry.py`
  - Stores registered agent cards in memory
  - Lets specialist servers register themselves at startup
  - Lets the host discover agents dynamically

- `remote_agent_connections.py`
  - Loads agent cards from the registry
  - Falls back to direct URL discovery when helpful
  - Caches A2A clients
  - Preserves remote task and context IDs across calls

- `host_agent.py`
  - Turns discovered agent cards into prompt text
  - Creates the `call_agent` LangChain tool

- `langgraph_a2a_agent.py`
  - Builds the LangGraph host agent
  - Refreshes discovered agents while the host is running
  - Delegates work through LangChain tools backed by the A2A SDK

- `city_agent/`
  - Structured-output city recommendation service on port `9997`

- `clothes_agent/`
  - Tool-based clothing recommendation service on port `9998`

- `weather_agent/`
  - Tool-based weather service on port `9999`

## Architecture

```text
User Query
   |
langgraph_a2a_agent.py
   |- asks remote_agent_connections.py for available agents
   |- remote_agent_connections.py checks agent_registry.py
   |- host prompt is rebuilt from discovered agent cards
   \- delegates to the selected specialist agent
      |- city_agent/
      |- clothes_agent/
      \- weather_agent/
```

## Discovery Flow

1. A specialist server starts.
2. It publishes its own public agent card at `/.well-known/agent-card.json`.
3. It registers that same card with `agent_registry.py`.
4. The host queries the registry to learn which agents are available.
5. The host builds its system prompt from the discovered agent cards.
6. When the model chooses `call_agent`, the host sends an A2A request to the selected specialist.

## How to Run

### 1. Start the registry

```bash
uv run langChain/agents/a2a/agent_registry.py
```

### 2. Start the specialist agents

Run each in a separate terminal:

```bash
uv run langChain/agents/a2a/city_agent/city_server.py
uv run langChain/agents/a2a/clothes_agent/clothes_server.py
uv run langChain/agents/a2a/weather_agent/weather_server.py
```

### 3. Start the LangGraph host

```bash
uv run langChain/agents/a2a/langgraph_a2a_agent.py
```

## Endpoints

### Registry endpoints

- `GET /registry/agents`: list all registered agent cards
- `POST /registry/register`: register or update one agent card
- `GET /health`: confirm the registry is running

### Specialist agent endpoints

- `GET /.well-known/agent-card.json`: public agent card discovery
- `POST /`: A2A JSON-RPC message processing

## Key Concepts

- Dynamic agent discovery through a simple registry
- Public A2A agent cards published by each specialist
- Remote tool calls through the A2A SDK
- LangGraph orchestration across specialist services
- Connection reuse through cached A2A clients
- Mixed specialist styles: structured output and tool-backed agents

## Troubleshooting

- If the host cannot find agents, make sure `agent_registry.py` is running on port `9990`.
- If an agent does not appear in the registry, restart that specialist server and look for its registration print message.
- If the host still cannot call an agent, confirm the specialist server is running on its expected port: `9997`, `9998`, or `9999`.
- If a port is already in use, stop the conflicting process or update the corresponding server configuration.
- If responses look weak or inconsistent, remember these are workshop examples with intentionally lightweight prompts and demo logic.

## Suggested Study Order

1. `agent_registry.py`
2. `remote_agent_connections.py`
3. `city_agent/`
4. `clothes_agent/`
5. `weather_agent/`
6. `host_agent.py`
7. `langgraph_a2a_agent.py`

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)
