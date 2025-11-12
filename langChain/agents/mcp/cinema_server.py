from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cinema", host="localhost",port=8001,stateless_http=True,mount_path="/mcp")

@mcp.tool()
async def get_movies(city:str, date:str) -> list[str]:
    """ Gets the current movies available for a given date """

    return ['Mission: Impossible','Home','Summer Love']

if __name__ == "__main__":
    try:
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("Closing server")
    finally:
        print("Server closed")