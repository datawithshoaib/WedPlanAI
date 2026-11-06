"""ASGI entry point: ``uv run uvicorn wedplanner.api.main:app --reload --port 8000``."""

import logging

from .app import create_app

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = create_app()
