"""WedPlannerAI: a multi-agent wedding planner."""

__version__ = "0.2.0"

from .brief import WeddingBrief  # noqa: E402
from .config import PlannerSettings  # noqa: E402
from .planner import GeneratedPlan, WeddingPlanner  # noqa: E402

__all__ = ["GeneratedPlan", "PlannerSettings", "WeddingBrief", "WeddingPlanner", "__version__"]
