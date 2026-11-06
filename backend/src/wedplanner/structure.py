"""Structured extraction from a finished wedding plan.

The planner agent writes freeform markdown. A separate, best-effort extraction pass
turns that markdown into typed fields so the frontend can render an "at a glance"
dashboard (budget, timeline, risks, vendors). If extraction fails, callers fall back
to markdown-only rendering.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from .config import PlannerSettings
from .llm import create_chat_model
from .prompts import EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

MAX_EXTRACTION_CHARS = 14000


class VenueRecommendation(BaseModel):
    name: str = ""
    location: str = ""
    why_it_fits: str = ""


class VendorRecommendation(BaseModel):
    category: str = ""
    name: str = ""
    why_recommended: str = ""


class BudgetItem(BaseModel):
    category: str = ""
    amount: float = 0.0
    currency: str = "USD"
    share_percent: float = 0.0


class TimelineMilestone(BaseModel):
    phase: str = ""
    horizon: str = ""
    actions: list[str] = Field(default_factory=list)


class RiskItem(BaseModel):
    risk: str = ""
    mitigation: str = ""


class PlanStructure(BaseModel):
    """Structured fields extracted from the freeform markdown plan."""

    executive_summary: str = Field(default="", description="One-paragraph summary of the plan.")
    venue_recommendations: list[VenueRecommendation] = Field(default_factory=list)
    vendor_recommendations: list[VendorRecommendation] = Field(default_factory=list)
    budget_allocation: list[BudgetItem] = Field(default_factory=list)
    timeline: list[TimelineMilestone] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return not any(
            [
                self.executive_summary,
                self.venue_recommendations,
                self.vendor_recommendations,
                self.budget_allocation,
                self.timeline,
                self.risks,
                self.open_questions,
            ]
        )


def normalize_structure(structure: PlanStructure, currency: str) -> PlanStructure:
    """Force the brief's currency and fill in missing budget shares."""
    total = sum(max(item.amount, 0) for item in structure.budget_allocation)
    for item in structure.budget_allocation:
        item.currency = currency
        item.amount = max(item.amount, 0)
        if item.share_percent <= 0 and total > 0:
            item.share_percent = round(item.amount / total * 100, 1)
        item.share_percent = min(item.share_percent, 100)
    return structure


def extract_structure(
    content: str, settings: PlannerSettings, currency: str = "USD"
) -> PlanStructure | None:
    """Best-effort extraction of structured fields from a finished plan."""
    try:
        model = create_chat_model(settings).with_structured_output(PlanStructure)
        result = model.invoke(
            f"{EXTRACTION_PROMPT.format(currency=currency)}\n\n---\nWedding plan:\n"
            f"{content[:MAX_EXTRACTION_CHARS]}"
        )
    except Exception as exc:  # noqa: BLE001 - extraction is optional
        logger.warning("Structured extraction failed; returning markdown only: %s", exc)
        return None
    if not isinstance(result, PlanStructure) or result.is_empty():
        return None
    return normalize_structure(result, currency)
