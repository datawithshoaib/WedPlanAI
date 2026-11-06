"""Research workers exposed to the planning agent as tools.

Each worker runs one web search and condenses the results with a small LLM call, so
the main agent receives short, sourced findings instead of raw search dumps.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from langchain.tools import BaseTool, tool
from langchain_core.messages import HumanMessage

from ..config import PlannerSettings
from ..llm import create_chat_model, message_text
from ..progress import ProgressCallback, ProgressEvent, Stage, noop_progress
from ..prompts import LOGISTICS_WORKER_PROMPT, VENUE_WORKER_PROMPT
from .search import SearchFn, build_search

logger = logging.getLogger(__name__)

WORKER_MAX_TOKENS = 1200

Worker = Callable[[str], str]


def build_worker(
    settings: PlannerSettings,
    persona: str,
    search: SearchFn,
    stage: Stage,
    label: str,
    on_progress: ProgressCallback,
) -> Worker:
    model = create_chat_model(settings, max_tokens=WORKER_MAX_TOKENS)

    def run(query: str) -> str:
        on_progress(ProgressEvent(stage=stage, status="started", message=f"Researching {label}"))
        try:
            digest = search(query)
            prompt = (
                f"{persona}\n\nResearch task: {query}\n\nSearch digest:\n{digest}\n\n"
                "Now write your concise findings."
            )
            findings = message_text(model.invoke([HumanMessage(content=prompt)]))
        except Exception as exc:
            logger.exception("Research worker '%s' failed", stage)
            on_progress(ProgressEvent(stage=stage, status="failed", message=str(exc)[:200]))
            return (
                f"Research on {label} failed ({type(exc).__name__}). "
                "Plan from general knowledge and tell the couple what to verify."
            )
        on_progress(ProgressEvent(stage=stage, status="completed", message=f"Finished {label}"))
        # Fall back to the raw digest if the model returned no visible text.
        return findings or digest

    return run


def build_research_tools(
    settings: PlannerSettings, on_progress: ProgressCallback = noop_progress
) -> list[BaseTool]:
    search = build_search(settings)
    venues = build_worker(
        settings, VENUE_WORKER_PROMPT, search, "research_venues", "venues and vendors", on_progress
    )
    logistics = build_worker(
        settings,
        LOGISTICS_WORKER_PROMPT,
        search,
        "research_logistics",
        "logistics and market pricing",
        on_progress,
    )

    @tool
    def research_venues_and_vendors(query: str) -> str:
        """Research wedding venues and vendors (caterers, photographers, florists, music)
        for the couple. Pass one detailed search query."""
        return venues(query)

    @tool
    def research_logistics_and_market(query: str) -> str:
        """Research wedding logistics and local market context (pricing, season, travel,
        accommodation, permits, risks). Pass one detailed search query."""
        return logistics(query)

    return [research_venues_and_vendors, research_logistics_and_market]
