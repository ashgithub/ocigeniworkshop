from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bill_server")

# MCP Servers reference: https://modelcontextprotocol.io/docs/learn/server-concepts
# Build an MCP server: https://modelcontextprotocol.io/docs/develop/build-server

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
        # mcp.run(transport="sse")
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("Closing server")
    finally:
        print("Server closed")