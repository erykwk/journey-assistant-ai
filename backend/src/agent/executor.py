from typing import Any

from google.genai import types
from pydantic import BaseModel, Field, ValidationError

from src.agent.llm_client import (
    GeminiEmptyResponseError,
    generate_response,
)
from src.agent.mcp_client import MCPToolError, call_tool

MAX_TOOL_CALLS = 5


class AgentExecutionError(RuntimeError):
    pass


class WeatherArguments(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


async def execute_agent(contents: list[types.Content]) -> str:
    tool_calls = 0

    while True:
        response = await generate_response(contents)
        candidate = response.candidates[0] if response.candidates else None
        candidate_content = candidate.content if candidate else None
        parts = candidate_content.parts if candidate_content else []
        function_calls = [
            part.function_call for part in parts if part.function_call is not None
        ]

        if not function_calls:
            if not response.text:
                raise GeminiEmptyResponseError("Gemini returned an empty response.")
            return response.text

        if tool_calls + len(function_calls) > MAX_TOOL_CALLS:
            raise AgentExecutionError("Gemini exceeded the tool-call limit.")

        if candidate_content is None:
            raise GeminiEmptyResponseError("Gemini returned an empty response.")
        contents.append(candidate_content)

        function_responses = []
        for function_call in function_calls:
            if function_call.name != "get_weather_forecast":
                raise AgentExecutionError(
                    f"Gemini requested an unsupported tool: {function_call.name}."
                )

            try:
                arguments = WeatherArguments.model_validate(
                    function_call.args or {},
                )
            except ValidationError as exc:
                raise AgentExecutionError(
                    "Gemini returned invalid weather tool arguments."
                ) from exc

            try:
                result: dict[str, Any] = {
                    "result": await call_tool(
                        "get_weather_forecast",
                        arguments.model_dump(),
                    )
                }
            except MCPToolError as exc:
                result = {"error": str(exc)}

            function_responses.append(
                types.Part.from_function_response(
                    name="get_weather_forecast",
                    response=result,
                )
            )
            tool_calls += 1

        contents.append(
            types.Content(role="user", parts=function_responses)
        )
