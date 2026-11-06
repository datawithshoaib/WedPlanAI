"""Plan creation shared by the blocking and streaming endpoints."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from ..brief import WeddingBrief
from ..llm import ConfigurationError
from ..planner import PlanGenerationError, Planner
from ..progress import ProgressCallback, ProgressEvent, noop_progress
from ..storage import PlanRepository
from .schemas import PlanResponse

logger = logging.getLogger(__name__)


class PlanError(Exception):
    """A plan request failed; carries the HTTP status code to report."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def to_plan_response(record: dict) -> PlanResponse:
    return PlanResponse.model_validate(record)


def _classify(exc: Exception) -> PlanError:
    if isinstance(exc, ConfigurationError):
        return PlanError(503, str(exc))
    if isinstance(exc, PlanGenerationError):
        return PlanError(502, str(exc))
    name = type(exc).__name__
    if name == "RateLimitError":
        return PlanError(
            429, "The language model is rate limited right now. Wait a minute and try again."
        )
    if name in {"APITimeoutError", "APIConnectionError", "ReadTimeout", "ConnectTimeout"}:
        return PlanError(504, "The language model did not respond in time. Please try again.")
    if name == "AuthenticationError":
        return PlanError(503, "The server's GROQ_API_KEY was rejected by Groq.")
    if name == "GraphRecursionError":
        return PlanError(502, "The planner got stuck calling tools. Please try again.")
    return PlanError(500, f"Planner run failed: {name}: {str(exc)[:300]}")


def create_plan(
    brief: WeddingBrief,
    planner: Planner,
    repository: PlanRepository,
    on_progress: ProgressCallback = noop_progress,
) -> PlanResponse:
    """Generate, persist, and return a plan. Raises PlanError on failure."""
    try:
        generated = planner.run(brief, on_progress)
    except Exception as exc:
        logger.exception("Planner run failed")
        raise _classify(exc) from exc

    on_progress(ProgressEvent(stage="saving", status="started", message="Saving to history"))
    plan_id = uuid.uuid4().hex
    repository.insert(
        plan_id=plan_id,
        title=brief.title(),
        brief=brief.model_dump(mode="json"),
        requirements=brief.build_requirements(),
        content=generated.content,
        structure=generated.structure.model_dump() if generated.structure else None,
        duration_seconds=generated.duration_seconds,
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        word_count=len(generated.content.split()),
    )
    record = repository.get(plan_id)
    if record is None:  # pragma: no cover - defensive
        raise PlanError(500, "Plan generated but could not be saved.")
    on_progress(ProgressEvent(stage="saving", status="completed", message="Saved"))
    return to_plan_response(record)
