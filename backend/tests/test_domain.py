from __future__ import annotations

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from wedplanner.brief import WeddingBrief
from wedplanner.config import BACKEND_DIR, PlannerSettings
from wedplanner.options import default_brief
from wedplanner.planner import clean_plan_markdown
from wedplanner.research.search import format_digest
from wedplanner.structure import BudgetItem, PlanStructure, normalize_structure


def make_brief(**overrides) -> WeddingBrief:
    data = {
        "wedding_location": "Lisbon, Portugal",
        "wedding_date": date.today() + timedelta(days=100),
        **overrides,
    }
    return WeddingBrief.model_validate(data)


def test_default_brief_is_valid_and_in_the_future():
    brief = WeddingBrief.model_validate(default_brief())
    brief.validate_for_planning()
    assert brief.wedding_date > date.today()


def test_budget_order_is_enforced():
    with pytest.raises(ValidationError, match="budget_high"):
        make_brief(budget_low=50000, budget_high=10000)


def test_unknown_currency_rejected_and_case_normalised():
    with pytest.raises(ValidationError):
        make_brief(currency="XYZ")
    assert make_brief(currency="eur").currency == "EUR"


def test_past_date_rejected_only_for_planning():
    brief = make_brief(wedding_date=date.today() - timedelta(days=1))
    with pytest.raises(ValueError, match="future"):
        brief.validate_for_planning()


def test_lists_are_deduplicated_and_stripped():
    brief = make_brief(wedding_styles=[" Modern ", "Modern", "", "Garden"])
    assert brief.wedding_styles == ["Modern", "Garden"]


def test_requirements_keep_multiline_notes_and_key_facts():
    today = date(2026, 1, 1)
    brief = make_brief(
        wedding_date=date(2026, 7, 1),
        guest_count=100,
        budget_low=40000,
        budget_high=60000,
        must_haves="Line one\nLine two",
    )
    text = brief.build_requirements(today=today)
    assert "Lisbon, Portugal" in text
    assert "July 01, 2026 (about 25 weeks from today)" in text
    assert "USD 40,000 to 60,000" in text
    assert "~USD 500 per guest" in text
    assert "Line one\nLine two" in text


def test_title_falls_back_to_location():
    assert make_brief(couple_name="  ").title() == "Wedding in Lisbon, Portugal"


def test_clean_plan_markdown_strips_preamble():
    assert clean_plan_markdown("Sure! Here you go.\n\n## Executive Summary\nHi") == (
        "## Executive Summary\nHi"
    )
    assert clean_plan_markdown("  no sections  ") == "no sections"


def test_normalize_structure_forces_currency_and_fills_shares():
    structure = PlanStructure(
        budget_allocation=[
            BudgetItem(category="Venue", amount=30000, currency="USD"),
            BudgetItem(category="Food", amount=10000, currency="USD", share_percent=25),
        ]
    )
    result = normalize_structure(structure, "EUR")
    assert [item.currency for item in result.budget_allocation] == ["EUR", "EUR"]
    assert result.budget_allocation[0].share_percent == 75.0
    assert result.budget_allocation[1].share_percent == 25


def test_format_digest_skips_empty_results_and_includes_urls():
    digest = format_digest(
        [
            {"title": "Venue guide", "url": "https://example.com", "content": "Great  venues\n"},
            {"title": "", "content": ""},
        ]
    )
    assert digest == "- Venue guide (https://example.com)\n  Great venues"


def test_settings_resolve_relative_db_path_against_backend_dir():
    settings = PlannerSettings(_env_file=None, db_path="data/x.db")
    assert settings.db_path == (BACKEND_DIR / "data" / "x.db").resolve()
    assert not settings.planner_ready


def test_blank_keys_count_as_missing():
    settings = PlannerSettings(_env_file=None, groq_api_key="  ", tavily_api_key="")
    assert not settings.planner_ready and not settings.research_ready
