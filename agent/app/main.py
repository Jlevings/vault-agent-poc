"""FastAPI entrypoint for the AI agent."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .agent import AgentOrchestrator
from .logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Vault AI Agent", version="0.1.0")
agent = AgentOrchestrator()

TEMPLATE_DIR = Path(__file__).parent / "templates"


class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt to send to the AI agent.")


class ChatResponse(BaseModel):
    answer: str
    products: List[Dict[str, Any]]
    keywords: List[str]


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = (TEMPLATE_DIR / "index.html").read_text()
    return HTMLResponse(content=html)


@app.get("/healthz")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    logger.info("Received chat request")
    try:
        result = agent.handle_prompt(request.message.strip())
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to handle prompt")
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc
    return ChatResponse(**result)


@app.on_event("shutdown")
def shutdown_event() -> None:
    logger.info("Shutting down agent resources")
    agent.shutdown()
