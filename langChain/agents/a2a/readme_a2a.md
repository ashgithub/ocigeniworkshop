# A2A (Agent-to-Agent) Communication System

This folder demonstrates a complete A2A (Agent-to-Agent) communication system using OCI Generative AI. The system consists of specialized agents that register themselves with a central registry and communicate through standardized protocols.

## What is A2A?

A2A (Agent-to-Agent) communication allows AI agents to interact with each other through standardized protocols. This implementation includes:
- **Agent Registry**: Central discovery service for available agents
- **Specialized Agents**: City, clothes, and weather agents with specific expertise
- **Main Orchestrator**: Intelligent agent that routes queries to appropriate specialists
- **Optimized Communication**: High-performance client caching and timeout management

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment, DB details, and wallet path.
- `.env`: Load environment variables (e.g., API keys if needed).
- All agents use OCI Generative AI models (OpenAI, Grok, etc.)

## Files in this Folder

### Core Infrastructure
1. **agent_registry.py**: Central agent registry server
   - In-memory agent discovery service
   - REST API for agent registration and lookup
   - Runs on port 9990
   - How to run: `uv run langChain/agents/a2a/agent_registry.py`

2. **remote_agent_connections.py**: Optimized A2A communication layer
   - Client caching for maximum performance
   - Registry integration for dynamic discovery
   - Global timeout configuration
   - Used by main agent for calling specialists

### Specialized Agents
3. **city_agent/**: Intelligent city recommendation agent
   - Uses structured output for detailed city information
   - Provides location, population, and reasoning data
   - Runs on port 9997
   - How to run: `uv run langChain/agents/a2a/city_agent/city_server.py`

4. **clothes_agent/**: Clothing recommendation agent
   - Uses LangChain tools for weather-based suggestions
   - Considers temperature, conditions, and user preferences
   - Runs on port 9998
   - How to run: `uv run langChain/agents/a2a/clothes_agent/clothes_server.py`

5. **weather_agent/**: Weather information agent
   - Uses LangChain tools for weather data retrieval
   - Provides forecasts and conditions by zip code
   - Runs on port 9999
   - How to run: `uv run langChain/agents/a2a/weather_agent/weather_server.py`

### Main Orchestrator
6. **langgraph_a2a_agent.py**: Intelligent main agent
   - Dynamically discovers available agents from registry
   - Uses LangGraph for async tool calling
   - Routes queries to appropriate specialized agents
   - How to run: `uv run langChain/agents/a2a/langgraph_a2a_agent.py`

## Running the Complete System

1. **Start the registry** (in background):
   ```bash
   uv run langChain/agents/a2a/agent_registry.py
   ```

2. **Start the specialized agents** (each in separate terminals):
   ```bash
   # Terminal 1
   uv run langChain/agents/a2a/city_agent/city_server.py

   # Terminal 2
   uv run langChain/agents/a2a/clothes_agent/clothes_server.py

   # Terminal 3
   uv run langChain/agents/a2a/weather_agent/weather_server.py
   ```

3. **Run the main agent**:
   ```bash
   uv run langChain/agents/a2a/langgraph_a2a_agent.py
   ```

## Testing Individual Components

Each agent includes test clients for development:

```bash
# Test city agent
uv run langChain/agents/a2a/city_agent/test_client.py

# Test clothes agent
uv run langChain/agents/a2a/clothes_agent/test_client.py

# Test weather agent
uv run langChain/agents/a2a/weather_agent/test_client.py
```

## Key Concepts Demonstrated

- **Registry-Based Discovery**: Dynamic agent registration and lookup
- **Multiple Agent Types**: Structured output vs traditional tools
- **Client Caching**: Performance optimization through connection reuse
- **Async Communication**: Non-blocking agent-to-agent calls
- **LangGraph Integration**: Complex agent workflows with memory
- **A2A Protocol**: Standardized agent communication

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────────┐
│  Main Agent     │────│    Agent Registry   │
│  (LangGraph)    │    │     (Port 9990)    │
└─────────────────┘    └─────────────────────┘
          │                       │
          └───────────────────────┼───────────────────────┐
                                  │                       │
                    ┌─────────────┼─────────────┐ ┌───────┼─────────────┐
                    │  City Agent │            │ │ Weather Agent      │
                    │ (Port 9997) │            │ │ (Port 9999)        │
                    └─────────────┘            │ └─────────────────────┘
                                              │
                                    ┌─────────┼─────────────┐
                                    │ Clothes Agent        │
                                    │ (Port 9998)          │
                                    └──────────────────────┘
```

## Learning Tips

- Start with individual agent test clients to understand each agent's capabilities
- Run the registry first, then start agents to see automatic registration
- Experiment with different queries that combine multiple agent types
- Monitor agent registration through registry endpoints
- Try modifying agent logic (structured output vs tools) to understand differences

## Sample Queries

The main agent can handle complex queries that require multiple specialists:

- "What clothes should I wear on a trip to Oracle headquarters next week?"
- "Recommend a city for a tech conference and check the weather there"
- "What's the weather like and what should I wear in Chicago?"

## API Endpoints

### Registry (Port 9990)
- `GET /registry/agents`: List all registered agents
- `GET /health`: Health check

### Agents (Ports 9997-9999)
- `GET /.well-known/agent.json`: Agent card discovery
- `POST /message`: A2A message processing

## Resources

- [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/)
- [OCI Gen AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/how_to/custom_tools/)
- [Structured Output](https://python.langchain.com/docs/how_to/structured_output/)

## Slack Channels

- **#generative-ai-users**: For OCI Gen AI questions
- **#igiu-innovation-lab**: General project discussions
- **#igiu-ai-learning**: Help with environment setup

## Development Notes

- Agents automatically register with the registry on startup
- The main agent dynamically builds system prompts from registry data
- Client caching eliminates connection overhead for repeated calls
- All agents use OCI models with consistent configuration
- Error handling ensures system reliability when individual agents fail
