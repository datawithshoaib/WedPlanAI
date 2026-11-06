"""FastAPI application exposing the wedding planning service to the frontend."""

from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .. import __version__
from ..brief import WeddingBrief
from ..config import PlannerSettings, get_settings
from ..options import (
    CEREMONY_TYPES,
    CURRENCIES,
    PRIORITY_OPTIONS,
    STYLE_OPTIONS,
    TONE_OPTIONS,
    default_brief,
)
from ..planner import Planner, WeddingPlanner
from ..progress import ProgressEvent
from ..storage import PlanRepository
from .schemas import (
    ErrorMessage,
    HealthResponse,
    OptionsResponse,
    PlanMessage,
    PlanResponse,
    PlanSummary,
    PlanSummaryList,
    ProgressMessage,
)
from .service import PlanError, create_plan, to_plan_response

logger = logging.getLogger(__name__)


# --- dependencies -----------------------------------------------------------------


def get_app_settings(request: Request) -> PlannerSettings:
    return request.app.state.settings


def get_repository(request: Request) -> PlanRepository:
    return request.app.state.repository


def get_planner(request: Request) -> Planner:
    return request.app.state.planner


SettingsDep = Annotated[PlannerSettings, Depends(get_app_settings)]
RepositoryDep = Annotated[PlanRepository, Depends(get_repository)]
PlannerDep = Annotated[Planner, Depends(get_planner)]


def ready_brief(brief: WeddingBrief, settings: SettingsDep) -> WeddingBrief:
    """Validate that a brief can be planned right now (keys present, date not past)."""
    missing = [
        name
        for name, present in (
            ("GROQ_API_KEY", settings.planner_ready),
            ("TAVILY_API_KEY", settings.research_ready),
        )
        if not present
    ]
    if missing:
        raise HTTPException(503, f"Server is missing {', '.join(missing)}. Add it to backend/.env.")
    try:
        brief.validate_for_planning()
    except ValueError as exc:
        raise RequestValidationError(
            [{"type": "value_error", "loc": ("body", "wedding_date"), "msg": str(exc)}]
        ) from exc
    return brief


ReadyBriefDep = Annotated[WeddingBrief, Depends(ready_brief)]


# --- app factory ------------------------------------------------------------------


def create_app(
    settings: PlannerSettings | None = None,
    planner: Planner | None = None,
    repository: PlanRepository | None = None,
) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.repository = repository or PlanRepository(settings.db_path)
        app.state.planner = planner or WeddingPlanner(settings)
        logger.info(
            "Plans database: %s (%d saved plans) | model: %s | groq key: %s | tavily key: %s",
            app.state.repository.db_path,
            app.state.repository.count(),
            settings.model_name,
            "set" if settings.planner_ready else "MISSING",
            "set" if settings.research_ready else "MISSING",
        )
        yield

    app = FastAPI(
        title="WedPlannerAI API",
        description="REST API for the multi-agent wedding planning assistant.",
        version=__version__,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {"name": "WedPlannerAI API", "docs": "/docs", "health": "/api/health"}

    @app.get("/api/health", response_model=HealthResponse, tags=["meta"])
    def health(settings: SettingsDep, repository: RepositoryDep) -> HealthResponse:
        return HealthResponse(
            planner_ready=settings.planner_ready,
            research_ready=settings.research_ready,
            model=settings.model_name,
            plan_count=repository.count(),
        )

    @app.get("/api/options", response_model=OptionsResponse, tags=["brief"])
    def options() -> OptionsResponse:
        return OptionsResponse(
            ceremony_types=CEREMONY_TYPES,
            currencies=CURRENCIES,
            style_options=STYLE_OPTIONS,
            priority_options=PRIORITY_OPTIONS,
            tone_options=TONE_OPTIONS,
            default_brief=default_brief(),
        )

    @app.post("/api/plans", response_model=PlanResponse, status_code=201, tags=["plans"])
    def generate_plan(
        brief: ReadyBriefDep, planner: PlannerDep, repository: RepositoryDep
    ) -> PlanResponse:
        """Generate a plan and return it when finished (takes about a minute)."""
        try:
            return create_plan(brief, planner, repository)
        except PlanError as exc:
            raise HTTPException(exc.status_code, exc.detail) from exc

    @app.post(
        "/api/plans/stream",
        tags=["plans"],
        response_class=StreamingResponse,
        responses={200: {"content": {"application/x-ndjson": {}}}},
    )
    def generate_plan_stream(
        brief: ReadyBriefDep, planner: PlannerDep, repository: RepositoryDep
    ) -> StreamingResponse:
        """Generate a plan, streaming newline-delimited JSON messages.

        Each line is one of: ``{"type": "progress", "event": {...}}``,
        ``{"type": "plan", "plan": {...}}`` (last line on success), or
        ``{"type": "error", "status_code": int, "detail": str}`` (last line on failure).
        The plan is saved even if the client disconnects before it finishes.
        """
        messages: queue.Queue[str | None] = queue.Queue()

        def on_progress(event: ProgressEvent) -> None:
            messages.put(ProgressMessage(event=event).model_dump_json())

        def worker() -> None:
            try:
                plan = create_plan(brief, planner, repository, on_progress)
                messages.put(PlanMessage(plan=plan).model_dump_json())
            except PlanError as exc:
                messages.put(
                    ErrorMessage(status_code=exc.status_code, detail=exc.detail).model_dump_json()
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Unexpected streaming failure")
                messages.put(ErrorMessage(status_code=500, detail=str(exc)).model_dump_json())
            finally:
                messages.put(None)

        threading.Thread(target=worker, name="plan-generation", daemon=True).start()

        def lines() -> Iterator[str]:
            while (line := messages.get()) is not None:
                yield line + "\n"

        return StreamingResponse(
            lines(),
            media_type="application/x-ndjson",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.get("/api/plans", response_model=PlanSummaryList, tags=["plans"])
    def list_plans(
        repository: RepositoryDep,
        limit: Annotated[int, Query(ge=1, le=500)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> PlanSummaryList:
        return PlanSummaryList(
            plans=[PlanSummary(**row) for row in repository.list(limit, offset)],
            total=repository.count(),
        )

    @app.get("/api/plans/{plan_id}", response_model=PlanResponse, tags=["plans"])
    def get_plan(plan_id: str, repository: RepositoryDep) -> PlanResponse:
        record = repository.get(plan_id)
        if record is None:
            raise HTTPException(404, "Plan not found.")
        return to_plan_response(record)

    @app.delete("/api/plans/{plan_id}", status_code=204, tags=["plans"])
    def delete_plan(plan_id: str, repository: RepositoryDep) -> Response:
        if not repository.delete(plan_id):
            raise HTTPException(404, "Plan not found.")
        return Response(status_code=204)

    @app.delete("/api/plans", status_code=204, tags=["plans"])
    def clear_plans(repository: RepositoryDep) -> Response:
        repository.clear()
        return Response(status_code=204)

    return app
