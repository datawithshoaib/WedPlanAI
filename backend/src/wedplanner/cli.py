"""Command-line planner: ``uv run wedplanner [brief.json] [-o plan.md]``.

Without a brief file, the built-in sample brief is used.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from pydantic import ValidationError

from .brief import WeddingBrief
from .config import get_settings
from .options import default_brief
from .planner import WeddingPlanner
from .progress import ProgressEvent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wedplanner", description=__doc__)
    parser.add_argument("brief", nargs="?", type=Path, help="JSON file with the wedding brief")
    parser.add_argument("-o", "--output", type=Path, help="write the markdown plan to this file")
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug logging")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    try:
        data = json.loads(args.brief.read_text(encoding="utf-8")) if args.brief else default_brief()
        brief = WeddingBrief.model_validate(data)
        brief.validate_for_planning()
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        print(f"Invalid brief: {exc}", file=sys.stderr)
        return 2

    def on_progress(event: ProgressEvent) -> None:
        print(f"  [{event.stage}] {event.status}: {event.message}", file=sys.stderr)

    print(f"Planning: {brief.title()} ({brief.wedding_location})", file=sys.stderr)
    plan = WeddingPlanner(get_settings()).run(brief, on_progress)
    print(f"Done in {plan.duration_seconds:.1f}s", file=sys.stderr)

    if args.output:
        args.output.write_text(plan.content, encoding="utf-8")
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(plan.content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
