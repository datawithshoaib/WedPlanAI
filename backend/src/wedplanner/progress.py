"""Progress events emitted while a plan is being generated.

The planner reports what it is doing through a plain callback so that callers can
stream progress to a UI, log it, or ignore it.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel

Stage = Literal[
    "planning",
    "research_venues",
    "research_logistics",
    "writing",
    "structuring",
    "saving",
]
Status = Literal["started", "completed", "failed"]


class ProgressEvent(BaseModel):
    stage: Stage
    status: Status
    message: str = ""


ProgressCallback = Callable[[ProgressEvent], None]


def noop_progress(_: ProgressEvent) -> None:
    return None
