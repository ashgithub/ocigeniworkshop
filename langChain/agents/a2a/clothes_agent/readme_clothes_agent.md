# Clothes Agent

## Overview

The Clothes Agent is an A2A (agent-to-agent) service that recommends clothing and accessories based on conditions such as temperature, rain, and user preference. In this workshop, it serves as a tool-based recommendation example inside the A2A system.

## Role in the A2A System

This agent is one of the specialized services used by the main orchestrator.

- It registers itself with the shared registry at startup.
- It exposes an A2A endpoint that other agents can call.
- It is typically discovered and used by `langgraph_a2a_agent.py`.
- Default local port: `9998`

## Files in This Folder

- `agent_executor.py`
  - Builds the clothes recommendation agent.
  - Defines the clothing recommendation tool and request-handling logic.

- `clothes_server.py`
  - Starts the A2A server.
  - Publishes the agent card and registers with the central registry.

- `test_client.py`
  - Sends a local test request to the running Clothes Agent.
  - Useful for verifying server connectivity and response behavior.

## How the Agent Works

1. A request reaches the Clothes Agent through the A2A server.
2. The server forwards the request to `ClothesAgentExecutor`.
3. The executor passes the user input to a LangChain agent with a clothing recommendation tool.
4. The tool generates sample clothing and accessory suggestions.
5. The result is returned to the caller as the A2A response.

## Prerequisites

Before running this agent, make sure:

- `sandbox.yaml` is configured correctly.
- Any required environment variables are available in `.env`.
- The agent port (`9998`) is available.

## How to Run

### Start the agent server

```bash
uv run langChain/agents/a2a/clothes_agent/clothes_server.py
```

### Test the agent directly

In another terminal:

```bash
uv run langChain/agents/a2a/clothes_agent/test_client.py
```

### Use it through the main orchestrator

If the remote agents are running:

```bash
uv run langChain/agents/a2a/langgraph_a2a_agent.py
```

## Example Queries

Try prompts such as:

- "What clothes should I wear for a rainy day?"
- "Recommend clothing for cold weather"
- "What should I wear in hot sunny conditions?"

## Key Concepts Demonstrated

- **LangChain Tools**: Tool-based recommendation flow
- **A2A Protocol**: Agent-to-agent communication over HTTP
- **Published Agent Card**: Direct discovery through the standard A2A card route
- **Tool Calling**: Passing structured arguments into a recommendation function
- **Orchestrated Assistance**: Acting as a specialist used by another agent

## Troubleshooting

- **Agent does not appear in the orchestrator**
  - Make sure `clothes_server.py` is running on port `9998`.

- **Port 9998 is already in use**
  - Stop the conflicting process or change the configured port in `clothes_server.py`.

- **Configuration errors**
  - Confirm that `sandbox.yaml` exists and contains valid OCI settings.

- **Recommendations seem too simplistic**
  - This example uses demo logic in `agent_executor.py`; update the tool if you want richer behavior.

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)

## Slack Channels

- **#generative-ai-users**: OCI Generative AI questions
- **#igiu-innovation-lab**: General project discussions
- **#igiu-ai-learning**: Help with environment setup and workshop examples
