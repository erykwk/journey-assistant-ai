import os

from google import genai
from google.genai import types


class GeminiConfigurationError(RuntimeError):
    pass


class GeminiEmptyResponseError(RuntimeError):
    pass


WEATHER_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather_forecast",
            description=(
                "Get the current temperature and wind speed at geographic coordinates."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "latitude": types.Schema(
                        type=types.Type.NUMBER,
                        description="Latitude in degrees, from -90 to 90.",
                    ),
                    "longitude": types.Schema(
                        type=types.Type.NUMBER,
                        description="Longitude in degrees, from -180 to 180.",
                    ),
                },
                required=["latitude", "longitude"],
            ),
        ),
    ],
)


async def generate_response(
    contents: list[types.Content],
) -> types.GenerateContentResponse:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiConfigurationError(
            "Set GOOGLE_API_KEY or GEMINI_API_KEY to enable Gemini."
        )

    async with genai.Client(api_key=api_key).aio as client:
        response = await client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[WEATHER_TOOL],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True,
                ),
                http_options=types.HttpOptions(timeout=30_000)
            ),
        )

    return response
