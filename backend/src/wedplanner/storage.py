"""SQLite persistence for generated wedding plans (standard library only)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS plans (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    brief_json TEXT NOT NULL,
    requirements TEXT NOT NULL,
    content TEXT NOT NULL,
    structure_json TEXT,
    duration_seconds REAL NOT NULL,
    created_at TEXT NOT NULL,
    word_count INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_plans_created_at ON plans (created_at DESC);
"""

SUMMARY_COLUMNS = "id, title, brief_json, created_at, duration_seconds, word_count"


def _loads(raw: str | None) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


class PlanRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commits on success, rolls back on error
                yield conn
        finally:
            conn.close()

    @staticmethod
    def _summary(row: sqlite3.Row) -> dict[str, Any]:
        brief = _loads(row["brief_json"]) or {}
        return {
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "duration_seconds": row["duration_seconds"],
            "word_count": row["word_count"],
            "wedding_location": brief.get("wedding_location") or None,
            "wedding_date": brief.get("wedding_date") or None,
            "guest_count": brief.get("guest_count"),
        }

    def insert(
        self,
        *,
        plan_id: str,
        title: str,
        brief: dict[str, Any],
        requirements: str,
        content: str,
        structure: dict[str, Any] | None,
        duration_seconds: float,
        created_at: str,
        word_count: int,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO plans (
                    id, title, brief_json, requirements, content, structure_json,
                    duration_seconds, created_at, word_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    title,
                    json.dumps(brief, default=str),
                    requirements,
                    content,
                    json.dumps(structure, default=str) if structure is not None else None,
                    duration_seconds,
                    created_at,
                    word_count,
                ),
            )

    def list(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT {SUMMARY_COLUMNS} FROM plans ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [self._summary(row) for row in rows]

    def get(self, plan_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["brief"] = _loads(record.pop("brief_json"))
        record["structure"] = _loads(record.pop("structure_json"))
        return record

    def delete(self, plan_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
        return cursor.rowcount > 0

    def clear(self) -> int:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM plans")
        return cursor.rowcount

    def count(self) -> int:
        with self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0])
