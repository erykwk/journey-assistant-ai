from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
from google.genai import types
from fastapi.testclient import TestClient

from src.agent import llm_client
from src.main import app


class FakeModels:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    async def generate_content(self, **kwargs):
        self.request = kwargs
        self.requests.append(kwargs)
        return next(self.responses)


class FakeAsyncClient:
    def __init__(self, responses):
        self.models = FakeModels(responses)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None


def test_chat_calls_gemini_and_returns_assistant_message(monkeypatch):
    response = SimpleNamespace(
        text="Sunny, 20 C",
        candidates=[
            SimpleNamespace(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="Sunny, 20 C")],
                )
            )
        ],
    )
    fake_client = FakeAsyncClient([response])
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(
        llm_client.genai,
        "Client",
        lambda api_key: SimpleNamespace(aio=fake_client),
    )

    response = TestClient(app).post(
        "/api/v1/agent/chat",
        json={
            "messages": [
                {"role": "user", "content": "What is the weather?"},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": {
            "role": "assistant",
            "content": "Sunny, 20 C",
        },
    }
    request = fake_client.models.requests[0]
    assert request["model"] == "gemini-2.5-flash"
    assert request["contents"][0].role == "user"
    assert request["contents"][0].parts[0].text == "What is the weather?"
    assert request["config"].http_options.timeout == 30_000
    assert request["config"].tools[0].function_declarations[0].name == (
        "get_weather_forecast"
    )


def test_chat_calls_mcp_when_gemini_requests_weather(monkeypatch):
    function_call_response = SimpleNamespace(
        text=None,
        candidates=[
            SimpleNamespace(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name="get_weather_forecast",
                            args={"latitude": 52.2297, "longitude": 21.0122},
                        )
                    ],
                )
            )
        ],
    )
    final_response = SimpleNamespace(
        text="Warsaw is currently 15 C.",
        candidates=[
            SimpleNamespace(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="Warsaw is currently 15 C.")],
                )
            )
        ],
    )
    fake_client = FakeAsyncClient([function_call_response, final_response])
    mcp_call = AsyncMock(return_value="Temperatura: 15°C, Wiatr: 10 km/h")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(
        llm_client.genai,
        "Client",
        lambda api_key: SimpleNamespace(aio=fake_client),
    )
    monkeypatch.setattr("src.agent.executor.call_tool", mcp_call)

    response = TestClient(app).post(
        "/api/v1/agent/chat",
        json={
            "messages": [
                {"role": "user", "content": "What is the weather in Warsaw?"},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["response"]["content"] == "Warsaw is currently 15 C."
    mcp_call.assert_awaited_once_with(
        "get_weather_forecast",
        {"latitude": 52.2297, "longitude": 21.0122},
    )
    follow_up = fake_client.models.requests[1]["contents"]
    assert follow_up[-1].parts[0].function_response.response == {
        "result": "Temperatura: 15°C, Wiatr: 10 km/h"
    }


def test_chat_reports_missing_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = TestClient(app).post(
        "/api/v1/agent/chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Set GOOGLE_API_KEY or GEMINI_API_KEY to enable Gemini."
    )


def test_chat_reports_gemini_timeout(monkeypatch):
    monkeypatch.setattr(
        "src.api.agent.execute_agent",
        AsyncMock(side_effect=httpx.TimeoutException("request timed out")),
    )

    response = TestClient(app).post(
        "/api/v1/agent/chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )

    assert response.status_code == 504
    assert response.json()["detail"] == "The Gemini request timed out."
