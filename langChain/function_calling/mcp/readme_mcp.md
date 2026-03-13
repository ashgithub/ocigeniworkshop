# MCP (Model Context Protocol) Module

## Overview

This folder demonstrates how to create and use MCP servers with OCI-hosted LLM clients. MCP allows LLMs to interact with external tools and services through standardized protocols.

## What This Module Demonstrates

This MCP example set includes:

- **Weather Server**: HTTP-based MCP server for weather. Gets  alerts and forecasts from the actual US National Weather Service
- **Bill Server**: Local stdio MCP server for bill projection calculations
- **Manual MCP Integration**: LangChain model plus MCP tool loop
- **Automatic MCP Integration**: Agent-based MCP tool calling
- **Responses API MCP Integration**: Direct OpenAI Responses API + MCP workflow

## Environment Setup

- `sandbox.yaml`: Contains OCI configuration and related settings.
- `.env`: Loads environment variables if required.
- Ensure the necessary MCP servers are running before using the client examples.

## Files in This Folder

1. **`weather_mcp_server.py`**
   - HTTP-based MCP server providing weather tools
   - Exposes `get_alerts` and `get_forecast`
   - Run: `uv run langChain/function_calling/mcp/weather_mcp_server.py`

2. **`bill_mcp_server.py`**
   - Local stdio MCP server for bill calculations
   - Exposes `get_projection_bill`
   - Typically started automatically by an MCP client

3. **`langchain_mcp_manual.py`**
   - Demonstrates manual MCP tool orchestration with a LangChain model
   - Run: `uv run langChain/function_calling/mcp/langchain_mcp_manual.py`

4. **`langchain_mcp_auto.py`**
   - Demonstrates automatic MCP tool orchestration with a LangChain agent
   - Run: `uv run langChain/function_calling/mcp/langchain_mcp_auto.py`

5. **`openai_responses_mcp.py`**
   - Demonstrates direct MCP integration using the OCI-hosted OpenAI Responses API
   - Run: `uv run langChain/function_calling/mcp/openai_responses_mcp.py`

6. **`langchain_mcp.ipynb`**
   - Interactive notebook walkthrough of MCP setup, tool discovery, and usage
   - Run: open in Jupyter or VS Code and execute cells sequentially

7. **`test_mcp.py`**
   - Local test script for direct OCI OpenAI MCP experimentation
   - Treat as a developer-oriented example, not the primary workshop path

## Suggested Study Order

1. `weather_mcp_server.py`
2. `bill_mcp_server.py`
3. `langchain_mcp_manual.py`
4. `langchain_mcp_auto.py`
5. `openai_responses_mcp.py`
6. `langchain_mcp.ipynb`

## How to Run the Examples

### Recommended path

1. Start the weather MCP server:

```bash
uv run langChain/function_calling/mcp/weather_mcp_server.py
```

2. Run the manual or automatic LangChain MCP client:

```bash
uv run langChain/function_calling/mcp/langchain_mcp_manual.py
uv run langChain/function_calling/mcp/langchain_mcp_auto.py
```

3. If using the Responses API example and remote exposure is required, expose the weather server with ngrok:

```bash
ngrok http 8000 --host-header=localhost:8000
```

4. Then run:

```bash
uv run langChain/function_calling/mcp/openai_responses_mcp.py
```

## Key Concepts Demonstrated

- **Multiple Transport Types**: HTTP (remote) vs stdio (local) MCP servers
- **Tool Discovery**: Automatic retrieval of tools from MCP servers
- **Manual Tool Orchestration**: Explicit MCP tool-calling loop
- **Agent-Based Tool Use**: LangChain agent calling MCP tools automatically
- **Responses API Integration**: Direct remote MCP access from the OpenAI Responses API

## Troubleshooting

- **Weather queries fail**
  - Make sure `weather_mcp_server.py` is running on port `8000`.

- **Bill server is not found**
  - Check the `bill_server` command path in the MCP client config.

- **Responses API example cannot reach weather MCP**
  - Verify the ngrok tunnel URL and make sure the weather server is exposed correctly.

- **No tools are discovered**
  - Confirm that the MCP client transport configuration matches the server type.

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [Fast MCP](https://gofastmcp.com/getting-started/welcome)
- [LangChain MCP Documentation](https://docs.langchain.com/oss/python/langchain/mcp)
- [US National Weather Service API](https://www.weather.gov/documentation/services-web-api)

## Slack Channels

- **#generative-ai-users**: OCI Generative AI questions
- **#igiu-ai-learning**: Help with environment setup and running code
- **#igiu-innovation-lab**: General project discussions
