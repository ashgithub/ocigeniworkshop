# LangChain Agents Module

This directory contains examples that demonstrate how to build agents with LangChain and LangGraph using OCI Generative AI models. It also includes Langfuse tracing examples and an A2A (agent-to-agent) communication module.

## What You Will Learn

This module covers the following topics:

1. Creating a basic LangChain agent with custom tools by using `create_agent`
2. Building LangGraph workflows with conditional routing and tool execution
3. Integrating Langfuse tracing with both LangChain agents and LangGraph workflows
4. Exploring A2A communication between multiple specialized agents

OCI Generative AI provides OpenAI-compatible APIs that support features such as structured output, function calling, and reasoning. These examples primarily use the OCI OpenAI-compatible helper to access those capabilities.

## Environment Setup

- `sandbox.yaml`: Contains OCI configuration and related workshop settings.
- `.env`: Loads environment variables that may be required by some examples.
- Ensure you have access to OCI Generative AI services and valid authentication before running the examples.

## Langfuse Setup

Some examples in this folder use Langfuse for tracing.
1. create an account at https://langfuse.com/?tab=metrics
2. create an demo org & project
3. create your API keys 
4. Set the `.env` file  variables: `LANGFUSE_HOST`, `LANGFUSE_SK`, `LANGFUSE_PK`
5. Optionally add a unique user identifier or tag in the tracing metadata so you can find your runs more easily.
6. refer to https://langfuse.com/integrations/frameworks/langchain for details

See `langfuse_agent.py` and `langfuse_graph.py` for examples of trace metadata and callback configuration.

## A2A Setup

To run the A2A examples, start the registry and remote agents before running the main orchestrator.

1. Start the sample remote agents:
   - `uv run langChain/agents/a2a/weather_agent/weather_server.py`
   - `uv run langChain/agents/a2a/city_agent/city_server.py`
   - `uv run langChain/agents/a2a/clothes_agent/clothes_server.py`
2. Confirm that the running ports match the `remote_addresses` configuration in `langChain/agents/a2a/remote_agent_connections.py`.
3. Run the main orchestrator:
   - `uv run langChain/agents/a2a/langgraph_a2a_agent.py`

## Suggested Study Order

The examples are designed to build on one another.

1. **`agents.ipynb`**
   - Guided notebook walkthrough of the core agent patterns in this module
   - Covers basic LangChain agents, LangGraph workflows, Langfuse tracing, and advanced traced graph concepts
   - Best starting point if you want a notebook-based learning path

2. **`langchain_agent.py`**
   - Introduces custom tools and a simple LangChain agent created with `create_agent`
   - Shows streaming output, a single invocation, and inspection of the final message state

3. **`langgraph_agent.py`**
   - Demonstrates how to build a LangGraph workflow with tool-calling nodes and conditional edges
   - Useful for understanding graph-based orchestration compared with a single LangChain agent

4. **`langfuse_agent.py`**
   - Shows how to add Langfuse tracing to a LangChain agent
   - Demonstrates callback configuration and trace metadata

5. **`langfuse_graph.py`**
   - Demonstrates Langfuse tracing in a more advanced LangGraph workflow
   - Includes observation decorators and manual trace updates

6. **`a2a/`**
   - Contains a multi-agent example with specialized services and a LangGraph-based orchestrator
   - Start by reviewing the individual agent folders, then run the orchestrator
   - This part of the workshop is intentionally more script-driven because it requires multiple cooperating services to run in parallel

## Slack Channels

- `#generative-ai-users`: Questions about OCI Generative AI
- `#igiu-innovation-lab`: General project discussions
- `#igiu-ai-learning`: Help with the sandbox environment or workshop examples