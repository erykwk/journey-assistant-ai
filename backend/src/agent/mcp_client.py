import os
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent, Tool

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001/mcp")
MCP_TIMEOUT_SECONDS = 15.0


class MCPToolError(RuntimeError):
    pass


async def list_tools() -> list[Tool]:
    async with httpx.AsyncClient(timeout=MCP_TIMEOUT_SECONDS) as http_client:
        async with streamable_http_client(
            MCP_SERVER_URL,
            http_client=http_client,
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()
                return result.tools


async def call_tool(name: str, arguments: dict[str, Any]) -> str:
    async with httpx.AsyncClient(timeout=MCP_TIMEOUT_SECONDS) as http_client:
        async with streamable_http_client(
            MCP_SERVER_URL,
            http_client=http_client,
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)

    text_content = [
        block.text for block in result.content if isinstance(block, TextContent)
    ]
    if result.isError:
        detail = "\n".join(text_content) or "The MCP tool call failed."
        raise MCPToolError(detail)
    if not text_content:
        raise MCPToolError("The MCP tool returned no text content.")

    return "\n".join(text_content)
