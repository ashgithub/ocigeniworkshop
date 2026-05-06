# City Agent

## Overview

The City Agent is an A2A (agent-to-agent) service that recommends cities based on user goals or preferences. In this workshop, it is the structured-output example in the A2A system: instead of relying on a traditional tool call, it uses a typed Pydantic schema to generate a consistent response.

## Role in the A2A System

This agent is one of the specialized services used by the main orchestrator.

- It registers itself with the shared registry at startup.
- It also publishes its own public agent card at the standard A2A route.
- It exposes an A2A endpoint that other agents can call.
- It is typically discovered and used by `langgraph_a2a_agent.py`.
- Default local port: `9997`

## Files in This Folder

- `agent_executor.py`
  - Builds the city recommendation agent.
  - Defines the structured response schema and request-handling logic.

- `city_server.py`
  - Starts the A2A server.
  - Publishes the agent card and registers with the central registry.

- `test_client.py`
  - Sends a local test request to the running City Agent.
  - Useful for verifying server connectivity and response behavior.

## How the Agent Works

1. A request reaches the City Agent through the A2A server.
2. The server forwards the request to `CityAgentExecutor`.
3. The executor passes the user input to a structured-output LLM workflow.
4. The model returns a typed city recommendation shaped by the `CityRecommendation` schema.
5. The result is returned to the caller as the A2A response.

## Dynamic Discovery Flow

1. Start `agent_registry.py`.
2. Start `city_server.py`.
3. The city server registers its public agent card with the registry.
4. The host asks the registry which agents are available.
5. The host can then route city-related requests to this specialist.

## Prerequisites

Before running this agent, make sure:

- `sandbox.yaml` is configured correctly.
- Any required environment variables are available in `.env`.
- `agent_registry.py` is running if you want dynamic host discovery.
- The agent port (`9997`) is available.

## How to Run

### Start the agent server

```bash
uv run langChain/agents/a2a/city_agent/city_server.py
```

Optional check for registration:

```bash
http localhost:9990/registry/agents
```

### Test the agent directly

In another terminal:

```bash
uv run langChain/agents/a2a/city_agent/test_client.py
```

### Use it through the main orchestrator

If the remote agents are running:

```bash
uv run langChain/agents/a2a/langgraph_a2a_agent.py
```

## Example Queries

Try prompts such as:

- "Recommend a city for a tech conference"
- "Suggest a city for winter sports"
- "What city would be good for outdoor activities?"

## Key Concepts Demonstrated

- **Structured Output**: Use of a Pydantic model for predictable responses
- **A2A Protocol**: Agent-to-agent communication over HTTP
- **Published Agent Card**: Direct discovery through the standard A2A card route
- **Registry Registration**: Dynamic discovery through the shared workshop registry
- **LLM Orchestration**: Turning free-form requests into typed outputs
- **Type Safety**: Response validation through schema-driven generation

## API Endpoints

- `GET /.well-known/agent-card.json`: Agent card discovery
- `POST /`: A2A JSON-RPC message processing

## Registry Interaction

At startup, `city_server.py` sends its public agent card to:

- `POST http://localhost:9990/registry/register`

## Troubleshooting

- **Agent does not appear in the orchestrator**
  - Make sure `agent_registry.py` is running on port `9990`.
  - Make sure `city_server.py` is running on port `9997`.
  - Restart the city server and confirm the registration print appears.

- **Port 9997 is already in use**
  - Stop the conflicting process or change the configured port in `city_server.py`.

- **Configuration errors**
  - Confirm that `sandbox.yaml` exists and contains valid OCI settings.

- **Unexpected or weak recommendations**
  - Try changing the model in `agent_executor.py` or adjusting the prompt.

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [Structured Output](https://python.langchain.com/docs/how_to/structured_output/)

## Slack Channels

- **#generative-ai-users**: OCI Generative AI questions
- **#igiu-innovation-lab**: General project discussions
- **#igiu-ai-learning**: Help with environment setup and workshop examples
