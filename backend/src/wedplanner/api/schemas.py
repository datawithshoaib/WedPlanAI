"""Pydantic response schemas for the WedPlannerAI REST API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from ..progress import ProgressEvent
from ..structure import PlanStructure


class PlanResponse(BaseModel):
    """A generated wedding plan."""

    id: str
    title: str
    requirements: str
    content: str
    structure: PlanStructure | None = None
    duration_seconds: float = 0.0
    created_at: str
    word_count: int = 0
    brief: dict[str, Any] | None = None


class PlanSummary(BaseModel):
    """Lightweight plan listing entry (no full content)."""

    id: str
    title: str
    duration_seconds: float = 0.0
    created_at: str
    word_count: int = 0
    wedding_location: str | None = None
    wedding_date: str | None = None
    guest_count: int | None = None


class PlanSummaryList(BaseModel):
    plans: list[PlanSummary]
    total: int


class OptionsResponse(BaseModel):
    """Dropdown options so the UI never hard-codes choices."""

    ceremony_types: list[str]
    currencies: list[str]
    style_options: list[str]
    priority_options: list[str]
    tone_options: list[str]
    default_brief: dict[str, Any]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    planner_ready: bool
    research_ready: bool
    model: str
    plan_count: int


class ProgressMessage(BaseModel):
    type: Literal["progress"] = "progress"
    event: ProgressEvent


class PlanMessage(BaseModel):
    type: Literal["plan"] = "plan"
    plan: PlanResponse


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    status_code: int
    detail: str
