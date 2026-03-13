"""
What this file does:
Runs an MCP server that integrates with the US National Weather Service API to
provide weather alerts and forecasts over HTTP.

Documentation to reference:
- MCP Servers reference: https://modelcontextprotocol.io/docs/learn/server-concepts
- Build an MCP server: https://modelcontextprotocol.io/docs/develop/build-server
- US National Weather Service API: https://www.weather.gov/documentation/services-web-api

How to run the file:
uv run langChain/function_calling/mcp/weather_mcp_server.py

Important sections:
- Step 1: Initialize the MCP server with HTTP transport
- Step 2: Define helper functions for weather API access
- Step 3: Expose weather tools to MCP clients
- Step 4: Run the HTTP MCP server
"""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# MCP Servers reference: https://modelcontextprotocol.io/docs/learn/server-concepts
# Fast MCP: https://gofastmcp.com/getting-started/welcome

mcp = FastMCP("weather", host="localhost",port=8000,stateless_http=True,mount_path="/mcp")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Step 2: Helper function to make requests to the weather API
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

# Step 2: Helper function for formatting weather alerts
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

# Step 3: MCP tool exposed to the LLM for alerts
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

# Step 3: MCP tool exposed to the LLM for forecasts
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
        # Step 4: Run the MCP server on streamable HTTP transport.
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("Closing server")
    finally:
        print("Server closed")
