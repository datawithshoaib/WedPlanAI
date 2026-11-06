"""HTTP API. Run with: ``uv run uvicorn wedplanner.api.main:app --reload``."""

from .app import create_app

__all__ = ["create_app"]
