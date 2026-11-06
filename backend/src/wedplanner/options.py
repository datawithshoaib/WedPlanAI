"""Shared wedding planning options exposed to the frontend via the API."""

from datetime import date, timedelta
from typing import Any

CEREMONY_TYPES = [
    "Ceremony and reception",
    "Reception only",
    "Destination wedding",
    "Multi-day wedding",
    "Elopement plus celebration",
]

CURRENCIES = ["USD", "EUR", "GBP", "INR", "CAD", "AUD", "AED", "SGD", "NZD"]

STYLE_OPTIONS = [
    "Modern",
    "Romantic",
    "Classic",
    "Garden",
    "Minimal",
    "Luxury",
    "Cultural fusion",
    "Destination",
    "Eco-conscious",
    "Black tie",
]

PRIORITY_OPTIONS = [
    "Venue shortlist",
    "Vendor research",
    "Budget allocation",
    "Guest experience",
    "Timeline",
    "Design direction",
    "Risk management",
    "Travel logistics",
]

TONE_OPTIONS = [
    "Elegant and practical",
    "Luxury editorial",
    "Budget-conscious",
    "Warm and family-centered",
]

SAMPLE_LEAD_DAYS = 240


def default_brief(today: date | None = None) -> dict[str, Any]:
    """A realistic sample brief; the date is always ~8 months from today."""
    today = today or date.today()
    return {
        "wedding_date": (today + timedelta(days=SAMPLE_LEAD_DAYS)).isoformat(),
        "couple_name": "Amira and Noah",
        "wedding_location": "Chicago, Illinois",
        "guest_count": 120,
        "currency": "USD",
        "budget_low": 35000,
        "budget_high": 65000,
        "ceremony_type": "Ceremony and reception",
        "wedding_styles": ["Modern", "Romantic", "Cultural fusion"],
        "planning_priorities": [
            "Venue shortlist",
            "Vendor research",
            "Budget allocation",
            "Timeline",
        ],
        "tone": "Elegant and practical",
        "must_haves": (
            "Indoor-outdoor venue, strong vegetarian menu, live acoustic music, "
            "smooth guest transportation, and a photography-forward schedule."
        ),
        "constraints": (
            "Avoid venues more than 45 minutes from downtown. Keep the design elevated "
            "without relying on heavy floral spend."
        ),
        "traditions": (
            "Blend a short western ceremony with a family tea ceremony. Include space "
            "for speeches from both families."
        ),
    }
