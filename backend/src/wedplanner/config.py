"""Runtime configuration.

Settings are read from environment variables and from ``backend/.env``. Paths are
resolved relative to the backend directory, so the app behaves the same no matter
which directory it is launched from.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "openai/gpt-oss-120b"


class PlannerSettings(BaseSettings):
    """Configuration for the planner, its research workers, and the API."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    groq_api_key: str | None = None
    tavily_api_key: str | None = None

    model_name: str = Field(default=DEFAULT_MODEL, validation_alias="PLANNER_MODEL")
    # gpt-oss models spend tokens on hidden reasoning; "low" keeps runs fast and
    # well inside free-tier rate limits. Set to "" to use the provider default.
    reasoning_effort: str = Field(default="low", validation_alias="PLANNER_REASONING_EFFORT")
    llm_max_retries: int = Field(default=4, validation_alias="PLANNER_MAX_RETRIES")
    llm_timeout_seconds: float = Field(default=120.0, validation_alias="PLANNER_TIMEOUT")

    db_path: Path = Field(
        default=BACKEND_DIR / "data" / "planner.db", validation_alias="PLANNER_DB"
    )
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="CORS_ORIGINS",
    )

    @field_validator("groq_api_key", "tavily_api_key", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("db_path", mode="after")
    @classmethod
    def _resolve_db_path(cls, value: Path) -> Path:
        value = value.expanduser()
        return value if value.is_absolute() else (BACKEND_DIR / value).resolve()

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def planner_ready(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def research_ready(self) -> bool:
        return bool(self.tavily_api_key)

    @classmethod
    def from_environment(cls) -> PlannerSettings:
        return cls()


@lru_cache(maxsize=1)
def get_settings() -> PlannerSettings:
    return PlannerSettings()
