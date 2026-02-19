# MCP (Model Context Protocol) Servers

This folder demonstrates how to create and use MCP servers with OCI-hosted LLM clients. MCP allows LLMs to interact with external tools and services through standardized protocols.

## What are MCP Servers?

MCP (Model Context Protocol) servers expose tools and resources that can be used by AI agents. This folder contains examples of:
- **Weather Server**: HTTP-based server providing weather alerts and forecasts from the US National Weather Service
- **Bill Server**: Local stdio server for bill projection calculations
- *Remote MCP Servers Integration**: client that connects to remote MCP servers and uses their tools

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

3. **openai_responses_mcp.py**: Modern OCI Responses API sample
- Demonstrates MCP integration with `responses.create()` method
- Uses OCI Generative AI with direct MCP server calling
- How to run: `uv run langChain/function_calling/mcp/openai_responses_mcp.py`

4. **langchain_mcp.py**: LangChain client with manual agent execution
   - Demonstrates manual agent execution with MCP tools
   - Shows tool discovery and binding
- How to run: `uv run langChain/function_calling/mcp/langchain_mcp_manual.py`

5. **langchain_mcp.ipynb**: Jupyter notebook version of the MCP integration
   - Interactive cells demonstrating MCP setup and usage
   - Includes exercises for experimentation
   - How to run: Open in Jupyter/VS Code and run cells sequentially

## Running the Examples

### Modern Approach (Recommended)
1. **Start the weather server** (in background):
   ```bash
   uv run langChain/function_calling/mcp/weather_mcp_server.py
   ```

2. **Set up ngrok tunnel** (for remote access):
   ```bash
   ngrok http 8000 --host-header=localhost:8000
   ```

3. **Run the modern host client** (uses OpenAI Responses API):
   ```bash
   uv run langChain/function_calling/mcp/langchain_host_responses.py
   ```

### Legacy Approach
1. **Run the legacy host client** (manual agent execution):
   ```bash
   uv run langChain/function_calling/mcp/langchain_host.py
   ```

### Interactive Approach
- **Use the notebook**: Open `langchain_mcp.ipynb` in Jupyter/VS Code and run cells sequentially

## Key Concepts Demonstrated

- **Multiple Transport Types**: HTTP (remote) vs stdio (local) servers
- **Modern Responses API**: Direct MCP integration with `responses.create()` method
- **Tool Discovery**: Automatic detection of available tools from servers
- **Manual Agent Execution**: Step-by-step tool calling with MCP tools (legacy approach)
- **Error Handling**: Connection and tool execution error management

## Learning Tips

- Start with individual servers to understand each transport type
- Experiment with different queries that combine weather and bill tools
- Try running servers on different ports or configurations
- Test error scenarios when servers are unavailable

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [Fast MCP](https://gofastmcp.com/getting-started/welcome)
- [LangChain MCP Documentation](https://docs.langchain.com/oss/python/langchain/mcp)
- [US National Weather Service API](https://www.weather.gov/documentation/services-web-api)

## Slack Channels

- **#oci-ai-services**: For MCP server related questions
- **#generative-ai-users**: For OCI Gen AI questions
- **#igiu-ai-learning**: Help with environment setup
