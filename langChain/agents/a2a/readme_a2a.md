# A2A (Agent-to-Agent) Communication System

This folder contains the workshop A2A example built around direct agent-card
discovery. Each specialist agent publishes its own card, and the LangGraph host
resolves those cards from known agent URLs before delegating work.

## Main Pieces

- `remote_agent_connections.py`
  - Resolves agent cards directly from known URLs
  - Caches A2A clients
  - Preserves remote task and context IDs across calls

- `langgraph_a2a_agent.py`
  - Builds the LangGraph host agent
  - Loads remote agent metadata into the system prompt
  - Delegates work through LangChain tools backed by the A2A SDK

- `host_agent.py`
  - Shared host-side prompt and tool helpers

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
   |- resolves published agent cards from known URLs
   |- builds a system prompt from discovered agent metadata
   \- delegates to specialist agents through remote_agent_connections.py
      |- city_agent/
      |- clothes_agent/
      \- weather_agent/
```

## How to Run

### 1. Start the specialist agents

Run each in a separate terminal:

```bash
uv run langChain/agents/a2a/city_agent/city_server.py
uv run langChain/agents/a2a/clothes_agent/clothes_server.py
uv run langChain/agents/a2a/weather_agent/weather_server.py
```

### 2. Start the LangGraph host

```bash
uv run langChain/agents/a2a/langgraph_a2a_agent.py
```

## Endpoints

Each specialist agent publishes:

- `GET /.well-known/agent-card.json`: agent card discovery
- `POST /`: A2A JSON-RPC message processing

## Key Concepts

- Direct agent-card discovery from known URLs
- Remote tool calls through the A2A SDK
- LangGraph orchestration across specialist services
- Connection reuse through cached A2A clients
- Mixed specialist styles: structured output and tool-backed agents

## Troubleshooting

- If the host cannot find agents, confirm the specialist servers are running on
  ports `9997`, `9998`, and `9999`.
- If a port is already in use, stop the conflicting process or update the
  corresponding server configuration.
- If responses look weak or inconsistent, remember these are workshop examples
  with intentionally lightweight prompts and demo logic.

## Suggested Study Order

1. `remote_agent_connections.py`
2. `city_agent/`
3. `clothes_agent/`
4. `weather_agent/`
5. `host_agent.py`
6. `langgraph_a2a_agent.py`

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)
