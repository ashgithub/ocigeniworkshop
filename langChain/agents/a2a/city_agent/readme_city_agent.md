# City Agent

## Overview

The City Agent is an A2A (agent-to-agent) service that recommends cities based on user goals or preferences. In this workshop, it is the structured-output example in the A2A system: instead of relying on a traditional tool call, it uses a typed Pydantic schema to generate a consistent response.

## Role in the A2A System

This agent is one of the specialized services used by the main orchestrator.

- It registers itself with the shared registry at startup.
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

## Prerequisites

Before running this agent, make sure:

- `sandbox.yaml` is configured correctly.
- Any required environment variables are available in `.env`.
- The central registry is running if you want this agent to register itself.

Start the registry with:

```bash
uv run langChain/agents/a2a/agent_registry.py
```

## How to Run

### Start the agent server

```bash
uv run langChain/agents/a2a/city_agent/city_server.py
```

### Test the agent directly

In another terminal:

```bash
uv run langChain/agents/a2a/city_agent/test_client.py
```

### Use it through the main orchestrator

If the registry and all remote agents are running:

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
- **Registry Registration**: Automatic discovery through the shared registry
- **LLM Orchestration**: Turning free-form requests into typed outputs
- **Type Safety**: Response validation through schema-driven generation

## Troubleshooting

- **Agent does not appear in the orchestrator**
  - Make sure `agent_registry.py` is running before you start `city_server.py`.

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
