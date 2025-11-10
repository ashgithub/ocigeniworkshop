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
1. Set the LANGFUSE_HOST to the provided instance IP: ej. http://129.000.000.000:port
2. Go to the browser and access the instance URL provided, you should see a login page
3. Create a new user account with corporation email. **Make sure to save your password!**
4. Inside the interface, create a sample organization and a sample project (platform will request to do so)
5. Go to the sample organization settings and find the API key field.
6. Create a new API key. This will **display only once** the host, public and secret keys
7. Use the generated keys to set the `.env` variables and you are ready to go!

## Suggested Study Order and File Descriptions

The files are designed to build upon each other. Study them in this order for a progressive understanding:

1. **langchain_agent.py**: basics on how to declare a tool, how to use the openai helper to build a langChain agent. Make sure to understand the difference from the agent call and model calls. This agent is independient and manages three diferent sequence tools.