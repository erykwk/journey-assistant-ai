from mcp.server.fastmcp import FastMCP

from src.weather import fetch_weather

mcp = FastMCP(
    "travel-mcp-server",
    host="0.0.0.0",
    port=8001,
    json_response=True,
    stateless_http=True,
)


@mcp.tool()
async def get_weather_forecast(latitude: float, longitude: float) -> str:
    """Get the current temperature and wind speed for the provided coordinates."""
    return await fetch_weather(latitude, longitude)


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
