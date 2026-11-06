from __future__ import annotations

from collections.abc import Iterator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from wedplanner.api import create_app
from wedplanner.brief import WeddingBrief
from wedplanner.config import PlannerSettings
from wedplanner.planner import GeneratedPlan
from wedplanner.progress import ProgressCallback, ProgressEvent, noop_progress
from wedplanner.storage import PlanRepository
from wedplanner.structure import BudgetItem, PlanStructure

SAMPLE_PLAN = """## Executive Summary
A modern, romantic celebration.

## Venue and Vendor Recommendations
- Venue A

## Budget Allocation
| Category | Amount | Share |
|---|---|---|
| Venue | 20000 | 40% |

## Timeline
1. Now - book venue

## Risks and Tradeoffs
- Weather

## Open Questions
- Final guest count?
"""


class FakePlanner:
    """Stands in for the LLM agent stack; records the briefs it was given."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.briefs: list[WeddingBrief] = []

    def run(self, brief: WeddingBrief, on_progress: ProgressCallback = noop_progress):
        self.briefs.append(brief)
        on_progress(ProgressEvent(stage="planning", status="started", message="Reading the brief"))
        if self.error:
            raise self.error
        on_progress(ProgressEvent(stage="writing", status="completed", message="Plan written"))
        structure = PlanStructure(
            executive_summary="A modern, romantic celebration.",
            budget_allocation=[BudgetItem(category="Venue", amount=20000, currency=brief.currency)],
        )
        return GeneratedPlan(content=SAMPLE_PLAN, structure=structure, duration_seconds=1.5)


@pytest.fixture
def settings(tmp_path) -> PlannerSettings:
    return PlannerSettings(
        _env_file=None,
        groq_api_key="test-groq",
        tavily_api_key="test-tavily",
        db_path=tmp_path / "plans.db",
    )


@pytest.fixture
def repository(settings) -> PlanRepository:
    return PlanRepository(settings.db_path)


@pytest.fixture
def planner() -> FakePlanner:
    return FakePlanner()


@pytest.fixture
def client(settings, planner, repository) -> Iterator[TestClient]:
    app = create_app(settings=settings, planner=planner, repository=repository)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def brief_payload() -> dict:
    return {
        "couple_name": "Amira and Noah",
        "wedding_location": "Chicago, Illinois",
        "wedding_date": (date.today() + timedelta(days=200)).isoformat(),
        "guest_count": 120,
        "currency": "USD",
        "budget_low": 35000,
        "budget_high": 65000,
        "wedding_styles": ["Modern", "Romantic"],
        "planning_priorities": ["Venue shortlist"],
        "must_haves": "Vegetarian menu\nLive music",
    }
