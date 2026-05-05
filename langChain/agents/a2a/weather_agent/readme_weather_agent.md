# Weather Agent

## Overview

The Weather Agent is an A2A (agent-to-agent) service that returns sample weather information for a location or zipcode. In this workshop, it serves as a tool-backed weather example that other agents can call as part of a larger workflow.

## Role in the A2A System

This agent is one of the specialized services used by the main orchestrator.

- It registers itself with the shared registry at startup.
- It exposes an A2A endpoint that other agents can call.
- It is typically discovered and used by `langgraph_a2a_agent.py`.
- Default local port: `9999`

## Files in This Folder

- `agent_executor.py`
  - Builds the weather agent.
  - Defines the sample weather tool and request-handling logic.

- `weather_server.py`
  - Starts the A2A server.
  - Publishes the agent card and registers with the central registry.

- `test_client.py`
  - Sends a local test request to the running Weather Agent.
  - Useful for verifying server connectivity and response behavior.

## How the Agent Works

1. A request reaches the Weather Agent through the A2A server.
2. The server forwards the request to `WeatherAgentExecutor`.
3. The executor passes the user input to a LangChain agent with a weather tool.
4. The tool generates sample weather output for the request.
5. The result is returned to the caller as the A2A response.

## Prerequisites

Before running this agent, make sure:

- `sandbox.yaml` is configured correctly.
- Any required environment variables are available in `.env`.
- The agent port (`9999`) is available.

## How to Run

### Start the agent server

```bash
uv run langChain/agents/a2a/weather_agent/weather_server.py
```

### Test the agent directly

In another terminal:

```bash
uv run langChain/agents/a2a/weather_agent/test_client.py
```

### Use it through the main orchestrator

If the remote agents are running:

```bash
uv run langChain/agents/a2a/langgraph_a2a_agent.py
```

## Example Queries

Try prompts such as:

- "What's the weather like in Chicago today?"
- "Give me the weather forecast for Denver"
- "Check weather conditions for zip code 60601"

## Key Concepts Demonstrated

- **LangChain Tools**: Tool-backed weather lookup flow
- **A2A Protocol**: Agent-to-agent communication over HTTP
- **Published Agent Card**: Direct discovery through the standard A2A card route
- **Tool Calling**: Converting a prompt into structured weather inputs
- **Specialized Services**: Acting as a weather expert inside a multi-agent system

## API Endpoints

- `GET /.well-known/agent-card.json`: Agent card discovery
- `POST /`: A2A JSON-RPC message processing

## Troubleshooting

- **Agent does not appear in the orchestrator**
  - Make sure `weather_server.py` is running on port `9999`.

- **Port 9999 is already in use**
  - Stop the conflicting process or change the configured port in `weather_server.py`.

- **Configuration errors**
  - Confirm that `sandbox.yaml` exists and contains valid OCI settings.

- **Weather output is not realistic**
  - This example uses simulated/demo weather logic in `agent_executor.py`; replace the tool logic if you want real API-backed weather data.

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)

## Slack Channels

- **#generative-ai-users**: OCI Generative AI questions
- **#igiu-innovation-lab**: General project discussions
- **#igiu-ai-learning**: Help with environment setup and workshop examples
