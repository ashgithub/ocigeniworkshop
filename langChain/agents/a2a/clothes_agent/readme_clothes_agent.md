# Clothes Agent

This folder contains the Clothes Agent, an A2A (Agent-to-Agent) server that provides clothing recommendation functionality using LangChain tools with OCI Generative AI.

## What is the Clothes Agent?

The Clothes Agent analyzes weather conditions and user preferences to provide appropriate clothing recommendations. It uses traditional LangChain tools to handle the logic of determining suitable clothing based on temperature, weather conditions, and user gender preferences.

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment, DB details, and wallet path.
- `.env`: Load environment variables (e.g., API keys if needed).

## Files in this Folder

1. **agent_executor.py**: Core agent logic using LangChain tools
   - Implements ClothesAgent class with LLM integration
   - Defines get_clothes tool for clothing recommendations
   - Handles A2A request/response processing
   - How to run: Used by clothes_server.py (not run directly)

2. **clothes_server.py**: A2A server implementation
   - FastAPI-based server on port 9998
   - Registers with central registry on startup
   - Handles incoming A2A messages
   - How to run: `uv run langChain/agents/a2a/clothes_agent/clothes_server.py`

3. **test_client.py**: Test client for development
   - Tests agent functionality with sample queries
   - Uses modern A2A client library
   - Demonstrates response handling
   - How to run: `uv run langChain/agents/a2a/clothes_agent/test_client.py`

## Running the Agent

1. **Start the agent server**:
   ```bash
   uv run langChain/agents/a2a/clothes_agent/clothes_server.py
   ```

2. **Test the agent** (in another terminal):
   ```bash
   uv run langChain/agents/a2a/clothes_agent/test_client.py
   ```

3. **Use with main agent**:
   - Ensure registry server is running on port 9990
   - Start main agent: `uv run langChain/agents/a2a/main.py`
   - Query like: "What clothes should I wear for a rainy day?"

## Key Concepts Demonstrated

- **LangChain Tools**: Traditional tool-based agent implementation
- **A2A Protocol**: Agent-to-agent communication via HTTP
- **Registry Integration**: Automatic registration on startup
- **LLM Integration**: OCI Generative AI for clothing recommendations
- **Tool Calling**: Function calling with structured parameters

## Sample Queries

The agent responds to queries like:
- "What clothes should I wear for a rainy day?"
- "Recommend clothing for cold weather"
- "What to wear in hot sunny conditions?"


## Learning Tips

- Start with the test client to understand agent responses
- Modify the get_clothes tool logic for different recommendations
- Experiment with different LLM models in agent_executor.py
- Test various weather conditions and user preferences

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [LangChain Tools](https://python.langchain.com/docs/how_to/custom_tools/)

## Slack Channels

- **#generative-ai-users**: For OCI Gen AI questions
- **#igiu-innovation-lab**: General project discussions
- **#igiu-ai-learning**: Help with environment setup
