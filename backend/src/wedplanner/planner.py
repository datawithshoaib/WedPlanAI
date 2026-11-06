"""The planning service: orchestrator agent + research workers + structured extraction."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from .brief import WeddingBrief
from .config import PlannerSettings
from .llm import create_chat_model, message_text
from .progress import ProgressCallback, ProgressEvent, noop_progress
from .prompts import WEDDING_PLANNER_SYSTEM_PROMPT, WEDDING_PLANNER_USER_PROMPT
from .research import build_research_tools
from .structure import PlanStructure, extract_structure

logger = logging.getLogger(__name__)

# Two tool calls + their results + the final answer fit comfortably in this budget,
# while still stopping a model that loops on tool calls.
AGENT_RECURSION_LIMIT = 12
FIRST_SECTION = "## Executive Summary"


class PlanGenerationError(RuntimeError):
    """The agent ran but did not produce a usable plan."""


@dataclass(frozen=True)
class GeneratedPlan:
    content: str
    structure: PlanStructure | None
    duration_seconds: float


class Planner(Protocol):
    """Anything that can turn a brief into a plan (real agent stack or a test fake)."""

    def run(
        self, brief: WeddingBrief, on_progress: ProgressCallback = noop_progress
    ) -> GeneratedPlan: ...


def clean_plan_markdown(content: str) -> str:
    """Drop any chatty preamble the model wrote before the first required section."""
    index = content.find(FIRST_SECTION)
    return content[index:].strip() if index > 0 else content.strip()


@dataclass(frozen=True)
class WeddingPlanner:
    """Composes and invokes the multi-agent planning workflow."""

    settings: PlannerSettings

    def generate(
        self,
        requirements: str,
        on_progress: ProgressCallback = noop_progress,
        today: date | None = None,
    ) -> str:
        today = today or date.today()
        tools = build_research_tools(self.settings, on_progress)
        agent = create_agent(
            model=create_chat_model(self.settings),
            tools=tools,
            name="MainWeddingPlannerAgent",
            system_prompt=WEDDING_PLANNER_SYSTEM_PROMPT.format(
                today=today.strftime("%B %d, %Y"), requirements=requirements
            ),
        )

        on_progress(ProgressEvent(stage="planning", status="started", message="Reading the brief"))
        research_tools = {tool.name for tool in tools}
        delegated = False
        writing_announced = False
        finished_tools: set[str] = set()
        final_text = ""

        def announce_writing() -> None:
            nonlocal writing_announced
            if not writing_announced:
                writing_announced = True
                on_progress(
                    ProgressEvent(stage="writing", status="started", message="Writing the plan")
                )

        # Stream state updates so we can tell the UI when research ends and writing begins.
        for update in agent.stream(
            {"messages": [HumanMessage(content=WEDDING_PLANNER_USER_PROMPT)]},
            config={"recursion_limit": AGENT_RECURSION_LIMIT},
            stream_mode="updates",
        ):
            for node_update in update.values():
                for message in (node_update or {}).get("messages", []):
                    if isinstance(message, ToolMessage):
                        finished_tools.add(message.name or "")
                        if research_tools <= finished_tools:
                            announce_writing()
                    elif isinstance(message, AIMessage):
                        if message.tool_calls:
                            if not delegated:
                                delegated = True
                                on_progress(
                                    ProgressEvent(
                                        stage="planning",
                                        status="completed",
                                        message="Delegated research to the worker agents",
                                    )
                                )
                            continue
                        announce_writing()
                        final_text = message_text(message) or final_text

        content = clean_plan_markdown(final_text)
        if not content:
            raise PlanGenerationError("The planner finished without writing a plan.")
        on_progress(ProgressEvent(stage="writing", status="completed", message="Plan written"))
        return content

    def run(
        self, brief: WeddingBrief, on_progress: ProgressCallback = noop_progress
    ) -> GeneratedPlan:
        started = time.perf_counter()
        content = self.generate(brief.build_requirements(), on_progress)

        on_progress(
            ProgressEvent(stage="structuring", status="started", message="Building the dashboard")
        )
        structure = extract_structure(content, self.settings, currency=brief.currency)
        on_progress(
            ProgressEvent(
                stage="structuring",
                status="completed" if structure else "failed",
                message="Dashboard ready" if structure else "Dashboard unavailable for this plan",
            )
        )
        return GeneratedPlan(
            content=content,
            structure=structure,
            duration_seconds=round(time.perf_counter() - started, 2),
        )
