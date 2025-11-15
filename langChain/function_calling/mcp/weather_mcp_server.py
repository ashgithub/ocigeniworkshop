"""
What this file does:
Demonstrates a complex MCP server that integrates with the US National Weather Service API to provide weather alerts and forecasts. This server is used by the 'langChain/function_calling/mcp/langchain_host.py' host to provide tool integration for weather data retrieval.

How to run the file:
uv run langChain/function_calling/mcp/weather_mcp_server.py

Documentation to reference:
- MCP Servers reference: https://modelcontextprotocol.io/docs/learn/server-concepts
- Build an MCP server: https://modelcontextprotocol.io/docs/develop/build-server
- US National Weather Service API: https://www.weather.gov/documentation/services-web-api

Comments on important sections of file:
- Step 1: Server initialization with HTTP transport on localhost:8000
- Step 2: Helper functions for API requests and data formatting
- Step 3: Tool definitions - get_alerts and get_forecast functions exposed to LLMs
- Step 4: Main execution block - runs the HTTP server until interrupted

Helpful notes:
- This server demonstrates external API integration in MCP
- Tools can be tested with queries like "give me weather alerts for CO" or "give me weather for latitude 37.7749, longitude -122.4194"
- The server runs on HTTP transport and can be accessed remotely at http://localhost:8000/mcp

Testing with cline: 

    "weather": {
      "url": "http://localhost:8000/mcp",
      "type": "streamableHttp",
      "disabled": false,
      "autoApprove": []
    },
1. ask a question what is weather in denver.
2. show me weather alerts for colorado
"""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# MCP Servers reference: https://modelcontextprotocol.io/docs/learn/server-concepts
# Build an MCP server: https://modelcontextprotocol.io/docs/develop/build-server

mcp = FastMCP("weather", host="localhost",port=8000,stateless_http=True,mount_path="/mcp")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Helper function to make request to weather API
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

# Helper function
def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
            Event: {props.get('event', 'Unknown')}
            Area: {props.get('areaDesc', 'Unknown')}
            Severity: {props.get('severity', 'Unknown')}
            Description: {props.get('description', 'No description available')}
            Instructions: {props.get('instruction', 'No specific instructions provided')}
            """

# Actual mcp tool exposed to the LLM
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

# Other tool exposed to LLM
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
                    {period['name']}:
                    Temperature: {period['temperature']}°{period['temperatureUnit']}
                    Wind: {period['windSpeed']} {period['windDirection']}
                    Forecast: {period['detailedForecast']}
                    """
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    try:
        # Running server on http transport
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("Closing server")
    finally:
        print("Server closed")
