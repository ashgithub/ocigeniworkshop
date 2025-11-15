## Welcome to the LangChain + LangGraph agent module

In this module, we will work formally with agents (LLMs using tools) with capabilities to solve complex user queries. Also we are exploring the LangFuse tracer to have better experience with debug and information from the develop side. Finally, and add-on of A2A protocol module to showcase the example of different agents communicating

In this module, we will explore the following capabilities:
1. Basic tool declaration and integration with the LangChain `create_agent` method
2. LangGraph agent method, inclusing conditions and workflows to the LLM
3. LangFuse tracing examples, from basic configuration along LangChain, to advanced features using a full LangGraph workflow
4. A2A communication capabilites, to connect three different agents that will inform the main orchestrator

OCI Gen AI provides OpenAI-compatible APIs that support advanced features like structured output, function calling, and reasoning. The module demonstrates both the OCI OpenAI-compatible library (best for OpenAI features) and LangChain OCI library (broader model support).

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment details.
- `.env`: Load environment variables (e.g., API keys if needed).
- Ensure you have access to OCI Generative AI services and proper authentication configured.
- Follow the instructions bellow to obtain the LangFuse keys:

### LangFuse Setup:
1. Set the LANGFUSE_HOST env variable to the provided instance IP: http://129.146.168.187:3000/
2. Go to the browser and access the instance URL provided, you should see a login page
3. Create a new user account with **corporation email**. **Make sure to use workshop_2025 as password**
4. Find **OciGenAIWorkshop** organization and accept memeber invitation. This could be in the messages / inbox profile section.
    - After you accept the invitation, you can navigate the org and look for the tracing, sessions, users and other features
    - If you don't have access, you can always create your own sample organization and project to use this features
5. Go to the **OciGenAIWorkshop** organization settings and find the API key field.
6. Create your own new API key. This will **display only once** the host, public and secret keys. **Make sure to have them the first time**
7. Use the generated keys to set the `.env` variables and you are ready to go!
    - To differenciate your tracings from other users, make sure to add a unique identificator over the tags metadata section.
    - `"langfuse_tags": ["workshop", "user-name"]      # Add tags to filter in the console. TODO: Add your own identificator to filter later on on the web interface`
    - Details on `langfuse_agent.py` on how to add tags and user information

### Important A2A setup
To be able to run the A2A module, it is required that you have first running the remote agents.
1. To run the available sample servers:
    - `uv run langChain/agents/a2a/weather_agent/weather_server.py`
    - `uv run langChain/agents/a2a/city_agent/city_server.py`
    - `uv run langChain/agents/a2a/clothes_agent/clothes_server.py`
2. Once the servers are running, checkout the running ports are the same as indicated in the `remote_addresses` dictionary from `remote_agent_connections.py`
    - This is important, if the weather port does not match, host agent will not be able to reach the remote.
3. Run the main agent with `uv run langChain/agents/a2a/main.py`

## Suggested Study Order and File Descriptions

The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **langchain_agent.py**: basics on how to declare a tool, how to use the openai helper to build a langChain agent. Make sure to understand the difference from the agent call and model calls. This agent is independient and manages three diferent sequence tools.

2. **langgraph_agent.py**: demonstrates building a LangGraph-based agent with tool-calling capabilities. Shows how to use LangGraph's StateGraph and conditional edges for more complex agent workflows compared to the simple create_agent approach.

3. **langfuse_agent.py**: shows how to integrate Langfuse tracing with LangChain agents. Demonstrates basic tracing setup, metadata configuration, and how to monitor agent tool calls and responses in the Langfuse dashboard.

4. **langfuse_graph.py**: advanced Langfuse integration with a complex LangGraph workflow. Shows observation decorators, manual trace updates, and multi-agent interactions with comprehensive tracing.

5. **a2a/**: explore agent-to-agent communication protocols. The a2a folder contains a complete multi-agent system with specialized agents that register with a central registry and communicate through standardized A2A protocols. Start with the individual agent servers, then run the main orchestrator.
