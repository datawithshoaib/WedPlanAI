"""Wedding brief domain model and the requirements text sent to the planner."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .options import CURRENCIES

LongText = Field(default="", max_length=2000)


class WeddingBrief(BaseModel):
    """Structured wedding requirements captured from the frontend form."""

    model_config = ConfigDict(str_strip_whitespace=True)

    couple_name: str = Field(default="", max_length=120)
    wedding_location: str = Field(min_length=2, max_length=200)
    wedding_date: date
    guest_count: int = Field(default=120, ge=2, le=2000)
    currency: str = "USD"
    budget_low: int = Field(default=35000, ge=0, le=100_000_000)
    budget_high: int = Field(default=65000, ge=0, le=100_000_000)
    ceremony_type: str = Field(default="Ceremony and reception", max_length=100)
    wedding_styles: list[str] = Field(default_factory=list, max_length=12)
    planning_priorities: list[str] = Field(default_factory=list, max_length=12)
    tone: str = Field(default="Elegant and practical", max_length=100)
    must_haves: str = LongText
    constraints: str = LongText
    traditions: str = LongText

    @field_validator("currency")
    @classmethod
    def _known_currency(cls, value: str) -> str:
        value = value.upper()
        if value not in CURRENCIES:
            raise ValueError(f"currency must be one of {', '.join(CURRENCIES)}")
        return value

    @field_validator("wedding_styles", "planning_priorities")
    @classmethod
    def _clean_list(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in values:
            item = item.strip()[:60]
            if item and item not in cleaned:
                cleaned.append(item)
        return cleaned

    @model_validator(mode="after")
    def _budget_order(self) -> WeddingBrief:
        if self.budget_high < self.budget_low:
            raise ValueError("budget_high must be greater than or equal to budget_low")
        return self

    def validate_for_planning(self, today: date | None = None) -> None:
        """Checks that only apply to new plans (stored briefs may be in the past)."""
        today = today or date.today()
        if self.wedding_date < today:
            raise ValueError("wedding_date must be today or in the future")

    def title(self) -> str:
        return self.couple_name or f"Wedding in {self.wedding_location}"

    def build_requirements(self, today: date | None = None) -> str:
        today = today or date.today()
        weeks_out = max(0, (self.wedding_date - today).days // 7)
        styles = ", ".join(self.wedding_styles) or "Flexible"
        priorities = ", ".join(self.planning_priorities) or "Balanced planning support"
        per_guest = (self.budget_low + self.budget_high) / 2 / max(self.guest_count, 1)

        lines = [
            f"Couple or event name: {self.couple_name or 'Not given'}",
            f"Wedding location: {self.wedding_location}",
            f"Target date: {self.wedding_date:%B %d, %Y} (about {weeks_out} weeks from today)",
            f"Guest count: {self.guest_count}",
            f"Budget range: {self.currency} {self.budget_low:,} to {self.budget_high:,} "
            f"(~{self.currency} {per_guest:,.0f} per guest at the midpoint)",
            f"Event scope: {self.ceremony_type}",
            f"Preferred style: {styles}",
            f"Planning priorities: {priorities}",
            f"Planner tone: {self.tone}",
            "",
            "Must-haves:",
            self.must_haves or "None specified.",
            "",
            "Constraints and sensitivities:",
            self.constraints or "None specified.",
            "",
            "Cultural, family, or ceremonial details:",
            self.traditions or "None specified.",
        ]
        return "\n".join(lines)
