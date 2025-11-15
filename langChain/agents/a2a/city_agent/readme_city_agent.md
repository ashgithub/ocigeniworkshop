# City Agent

This folder contains the City Agent, an A2A (Agent-to-Agent) server that provides intelligent city recommendation functionality using structured output from OCI Generative AI.

## What is the City Agent?

The City Agent analyzes user requests and provides thoughtful city recommendations with detailed information including location data, population, and reasoning for the recommendation. Instead of using traditional tools, it leverages structured output to generate consistent, typed responses.

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment, DB details, and wallet path.
- `.env`: Load environment variables (e.g., API keys if needed).

## Files in this Folder

1. **agent_executor.py**: Core agent logic using structured output
   - Implements CityAgent class with LLM integration
   - Defines CityRecommendation Pydantic model
   - Handles A2A request/response processing
   - How to run: Used by city_server.py (not run directly)

2. **city_server.py**: A2A server implementation
   - FastAPI-based server on port 9997
   - Registers with central registry on startup
   - Handles incoming A2A messages
   - How to run: `uv run langChain/agents/a2a/city_agent/city_server.py`

3. **test_client.py**: Test client for development
   - Tests agent functionality with sample queries
   - Uses modern A2A client library
   - Demonstrates structured response handling
   - How to run: `uv run langChain/agents/a2a/city_agent/test_client.py`

## Running the Agent

1. **Start the agent server**:
   ```bash
   uv run langChain/agents/a2a/city_agent/city_server.py
   ```

2. **Test the agent** (in another terminal):
   ```bash
   uv run langChain/agents/a2a/city_agent/test_client.py
   ```

3. **Use with main agent**:
   - Ensure registry server is running on port 9990
   - Start main agent: `uv run langChain/agents/a2a/main.py`
   - Query like: "Recommend a city for a tech conference"

## Key Concepts Demonstrated

- **Structured Output**: Using Pydantic models for consistent responses
- **A2A Protocol**: Agent-to-agent communication via HTTP
- **Registry Integration**: Automatic registration on startup
- **LLM Integration**: OCI Generative AI for intelligent recommendations
- **Type Safety**: Pydantic validation for response data

## Sample Queries

The agent responds to queries like:
- "Recommend a city for a tech conference"
- "What city would be good for outdoor activities?"
- "Suggest a city for winter sports"


## Learning Tips

- Start with the test client to understand agent responses
- Modify the CityRecommendation model to add more fields
- Experiment with different LLM models in agent_executor.py
- Test error scenarios and fallback responses

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)

## Slack Channels

- **#generative-ai-users**: For OCI Gen AI questions
- **#igiu-innovation-lab**: General project discussions
- **#igiu-ai-learning**: Help with environment setup
