import asyncio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types
from src.weather import fetch_weather

# Inicjalizacja serwera MCP
server = Server("travel-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Rejestruje dostępne narzędzia dla klienta MCP."""
    return [
        types.Tool(
            name="get_weather_forecast",
            description="Pobiera prognozę pogody (aktualna temperatura i wiatr) dla podanych współrzędnych.",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Szerokość geograficzna (np. 52.2297 dla Warszawy)"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Długość geograficzna (np. 21.0122 dla Warszawy)"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Obsługuje wywołania narzędzi ze strony klienta."""
    if name == "get_weather_forecast":
        lat = arguments.get("latitude")
        lon = arguments.get("longitude")
        
        try:
            weather_info = await fetch_weather(lat, lon)
            return [types.TextContent(type="text", text=weather_info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Błąd podczas pobierania pogody: {str(e)}")]
            
    raise ValueError(f"Nieznane narzędzie: {name}")

async def main():
    """Uruchamia serwer MCP na standardowym wejściu/wyjściu (stdio)."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="travel-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
