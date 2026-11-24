import pytest

from src.agent.mcp_client import call_tool, list_tools


@pytest.mark.asyncio
async def test_mcp_server_lists_weather_tool():
    tools = await list_tools()

    assert "get_weather_forecast" in {tool.name for tool in tools}


@pytest.mark.asyncio
async def test_mcp_server_calls_weather_tool():
    result = await call_tool(
        "get_weather_forecast",
        {"latitude": 52.2297, "longitude": 21.0122},
    )

    assert "Temperatura:" in result
    assert "Wiatr:" in result
