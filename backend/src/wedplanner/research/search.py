"""Tavily-backed web search that returns a compact, LLM-friendly digest."""

from __future__ import annotations

import logging
from collections.abc import Callable

from tavily import TavilyClient

from ..config import PlannerSettings
from ..llm import ConfigurationError

logger = logging.getLogger(__name__)

MAX_RESULTS = 6
SNIPPET_CHARS = 500
MAX_QUERY_CHARS = 380  # Tavily rejects queries longer than 400 characters.

SearchFn = Callable[[str], str]


def format_digest(results: list[dict], max_results: int = MAX_RESULTS) -> str:
    digest: list[str] = []
    for item in results[:max_results]:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        snippet = " ".join((item.get("content") or "").split())[:SNIPPET_CHARS]
        if not title and not snippet:
            continue
        entry = f"- {title or '(untitled)'}"
        if url:
            entry += f" ({url})"
        if snippet:
            entry += f"\n  {snippet}"
        digest.append(entry)
    return "\n\n".join(digest)


def build_search(settings: PlannerSettings) -> SearchFn:
    """Return a function that searches the web and never raises on provider errors."""
    if not settings.tavily_api_key:
        raise ConfigurationError("TAVILY_API_KEY is required for web research.")

    client = TavilyClient(api_key=settings.tavily_api_key)

    def search(query: str) -> str:
        query = " ".join(query.split())[:MAX_QUERY_CHARS]
        logger.info("Web search: %s", query)
        try:
            response = client.search(query, max_results=MAX_RESULTS, search_depth="basic")
        except Exception as exc:  # noqa: BLE001 - network/provider errors must not kill the run
            logger.warning("Web search failed: %s", exc)
            return f"Web search failed ({type(exc).__name__}). No live results are available."
        digest = format_digest(response.get("results") or [])
        return digest or f"No useful results found for: {query}"

    return search
