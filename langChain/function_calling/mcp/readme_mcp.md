# MCP (Model Context Protocol) Servers

This folder demonstrates how to create and use MCP servers with LangChain agents. MCP allows LLMs to interact with external tools and services through standardized protocols.

## What are MCP Servers?

MCP (Model Context Protocol) servers expose tools and resources that can be used by AI agents. This folder contains examples of:
- **Weather Server**: HTTP-based server providing weather alerts and forecasts from the US National Weather Service
- **Bill Server**: Local stdio server for bill projection calculations
- **Host Integration**: LangChain client that connects to MCP servers and uses their tools

## Environment Setup

- `sandbox.yaml`: Contains OCI config, compartment, and other settings
- `.env`: Load environment variables if needed
- Ensure MCP servers are running before using the host client

## Files in this Folder

1. **weather_mcp_server.py**: HTTP-based MCP server providing weather tools
   - Runs on localhost:8000
   - Provides `get_alerts` and `get_forecast` tools
   - How to run: `uv run langChain/function_calling/mcp/weather_mcp_server.py`

2. **bill_mcp_server.py**: Local MCP server for bill calculations
   - Uses stdio transport (started automatically by client)
   - Provides `get_projection_bill` tool
   - How to run: Started automatically by langchain_host.py

3. **langchain_host.py**: LangChain client that connects to MCP servers
   - Demonstrates manual agent execution with MCP tools
   - Shows tool discovery and binding
   - How to run: `uv run langChain/function_calling/mcp/langchain_host.py`

4. **langchain_host.ipynb**: Jupyter notebook version of the MCP integration
   - Interactive cells demonstrating MCP setup and usage
   - Includes exercises for experimentation
   - How to run: Open in Jupyter/VS Code and run cells sequentially

## Running the Examples

1. **Start the weather server** (in background):
   ```bash
   uv run langChain/function_calling/mcp/weather_mcp_server.py
   ```

2. **Run the host client**:
   ```bash
   uv run langChain/function_calling/mcp/langchain_host.py
   ```

3. **Or use the notebook**:
   - Open `langchain_host.ipynb` in Jupyter
   - Run cells in order

## Key Concepts Demonstrated

- **Multiple Transport Types**: HTTP (remote) vs stdio (local) servers
- **Tool Discovery**: Automatic detection of available tools from servers
- **Manual Agent Execution**: Step-by-step tool calling with MCP tools
- **Error Handling**: Connection and tool execution error management

## Learning Tips

- Start with individual servers to understand each transport type
- Experiment with different queries that combine weather and bill tools
- Try running servers on different ports or configurations
- Test error scenarios when servers are unavailable

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [LangChain MCP Documentation](https://docs.langchain.com/oss/python/langchain/mcp)
- [US National Weather Service API](https://www.weather.gov/documentation/services-web-api)

## Slack Channels

- **#oci-ai-services**: For MCP server related questions
- **#generative-ai-users**: For OCI Gen AI questions
- **#igiu-ai-learning**: Help with environment setup
