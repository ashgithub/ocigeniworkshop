"""
What this file does:
Demonstrates a simple MCP server that exposes a bill projection tool. This server is used by the 'langChain/function_calling/mcp/langchain_host.py' host to provide tool integration for calculating projected utility bills based on weather and appliance usage.

Documentation to reference:
- MCP Servers reference: https://modelcontextprotocol.io/docs/learn/server-concepts
- Fast MCP: https://gofastmcp.com/getting-started/welcome
Comments on important sections of file:
- Step 1: Server initialization with stdio transport (automatically launched by langchain_host.py)
- Step 2: Tool definition - get_projection_bill function exposed to LLMs
- Step 3: Main execution block - runs the server until interrupted


testing with cline. 

add to your cline mcp config: 

    "bill_server": {
      "disabled": false,
      "autoApprove": [],
      "type": "stdio",
      "command": "/Users/ashish/work/code/python/workshop/.venv/bin/python",
      "args": ["/Users/ashish/work/code/python/workshop/langChain/function_calling/mcp/bill_mcp_server.py"]
    }
    
ask a question like: what is my bill projection if weather is 40 and i have gas oven

"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bill_server")

# This is an stdio server, it will be automatically run by the MCP client (langchain_host.py) when tools are initialized.

# Local run tool exposed to the agent
@mcp.tool()
def get_projection_bill(current_weather: int, gas_oven: bool) -> int:
    """ Returns the projected bill for a user depending on the current one and if it has or not oven """
    if gas_oven:
        return (current_weather*2) + 45
    return (current_weather*2) + 4

if __name__ == "__main__":
    try:
        # transport methods http/sse for network connection
        # stdio for local machine MCP
        # mcp.run(transport="streamable-http")
        # mcp.run(transport="sse") # this is getting deprecated. do not use unless dealing with legacy code
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("Closing server")
    finally:
        print("Server closed")
