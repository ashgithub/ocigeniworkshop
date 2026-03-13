"""
What this file does:
Runs a simple MCP server that exposes a bill projection tool over stdio. This
server is intended to be launched by an MCP client so agents can call it as an
external tool.

Documentation to reference:
- MCP Servers reference: https://modelcontextprotocol.io/docs/learn/server-concepts
- Fast MCP: https://gofastmcp.com/getting-started/welcome

How to run the file:
This server is typically launched automatically by an MCP client via stdio.

Important sections:
- Step 1: Initialize the MCP server
- Step 2: Define the bill projection tool
- Step 3: Run the stdio server
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bill_server")

# Step 1: This stdio server is typically launched automatically by an MCP client.

# Step 2: Local tool exposed to the agent
@mcp.tool()
def get_projection_bill(current_weather: int, gas_oven: bool) -> int:
    """Return a projected bill based on weather and oven type."""
    if gas_oven:
        return (current_weather*2) + 45
    return (current_weather*2) + 4

if __name__ == "__main__":
    try:
        # Step 3: Run the server over stdio.
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("Closing server")
    finally:
        print("Server closed")
