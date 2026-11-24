from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field

from src.agent.llm_client import (
    GeminiConfigurationError,
    GeminiEmptyResponseError,
)
from src.agent.executor import AgentExecutionError, execute_agent
from src.agent.mcp_client import MCPToolError

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str


class ChatResponse(BaseModel):
    response: AssistantMessage


@router.post("/agent/chat", response_model=ChatResponse, tags=["Agent"])
async def chat(request: ChatRequest) -> ChatResponse:
    if not any(message.role == "user" for message in request.messages):
        raise HTTPException(
            status_code=422,
            detail="At least one user message is required.",
        )

    contents = [
        types.Content(
            role="model" if message.role == "assistant" else "user",
            parts=[types.Part.from_text(text=message.content)],
        )
        for message in request.messages
    ]

    try:
        answer = await execute_agent(contents)
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiEmptyResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AgentExecutionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except MCPToolError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (TimeoutError, httpx.TimeoutException) as exc:
        raise HTTPException(
            status_code=504,
            detail="The Gemini request timed out.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="A request to Gemini or the MCP server failed.",
        ) from exc
    except APIError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"The Gemini API request failed: {exc}",
        ) from exc

    return ChatResponse(response=AssistantMessage(content=answer))