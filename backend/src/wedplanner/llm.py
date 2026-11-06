"""Chat model factory and message helpers."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq

from .config import PlannerSettings


class ConfigurationError(RuntimeError):
    """Raised when a required API key or setting is missing."""


def create_chat_model(settings: PlannerSettings, **overrides: Any) -> ChatGroq:
    if not settings.groq_api_key:
        raise ConfigurationError("GROQ_API_KEY is required to run the planner.")

    kwargs: dict[str, Any] = {
        "model": settings.model_name,
        "api_key": settings.groq_api_key,
        "max_retries": settings.llm_max_retries,
        "timeout": settings.llm_timeout_seconds,
    }
    if settings.reasoning_effort and settings.model_name.startswith("openai/gpt-oss"):
        kwargs["reasoning_effort"] = settings.reasoning_effort
    kwargs.update(overrides)
    return ChatGroq(**kwargs)


def message_text(message: BaseMessage) -> str:
    """Return a message's text whether its content is a string or a list of blocks."""
    return message.text.strip()
