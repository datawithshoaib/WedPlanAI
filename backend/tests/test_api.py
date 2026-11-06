from __future__ import annotations

import json
from datetime import date, timedelta

from fastapi.testclient import TestClient

from wedplanner.api import create_app
from wedplanner.config import PlannerSettings
from wedplanner.llm import ConfigurationError

from .conftest import FakePlanner


def test_health_reports_readiness(client):
    body = client.get("/api/health").json()
    assert body["planner_ready"] and body["research_ready"]
    assert body["plan_count"] == 0


def test_options_include_fresh_default_brief(client):
    body = client.get("/api/options").json()
    assert "USD" in body["currencies"]
    assert body["default_brief"]["wedding_date"] > date.today().isoformat()


def test_create_list_get_delete_plan(client, brief_payload, planner):
    created = client.post("/api/plans", json=brief_payload)
    assert created.status_code == 201, created.text
    plan = created.json()
    assert plan["title"] == "Amira and Noah"
    assert plan["structure"]["budget_allocation"][0]["amount"] == 20000
    assert plan["word_count"] > 0
    assert "Vegetarian menu\nLive music" in plan["requirements"]
    assert planner.briefs[0].wedding_location == "Chicago, Illinois"

    listing = client.get("/api/plans").json()
    assert listing["total"] == 1
    summary = listing["plans"][0]
    assert summary["wedding_location"] == "Chicago, Illinois"
    assert summary["guest_count"] == 120

    fetched = client.get(f"/api/plans/{plan['id']}").json()
    assert fetched["content"] == plan["content"]
    assert fetched["brief"]["budget_high"] == 65000

    assert client.delete(f"/api/plans/{plan['id']}").status_code == 204
    assert client.get(f"/api/plans/{plan['id']}").status_code == 404
    assert client.delete(f"/api/plans/{plan['id']}").status_code == 404


def test_clear_plans(client, brief_payload):
    client.post("/api/plans", json=brief_payload)
    client.post("/api/plans", json=brief_payload)
    assert client.delete("/api/plans").status_code == 204
    assert client.get("/api/plans").json()["total"] == 0


def test_validation_errors(client, brief_payload):
    bad_budget = {**brief_payload, "budget_low": 90000}
    assert client.post("/api/plans", json=bad_budget).status_code == 422

    past = {**brief_payload, "wedding_date": (date.today() - timedelta(days=3)).isoformat()}
    response = client.post("/api/plans", json=past)
    assert response.status_code == 422
    assert "future" in json.dumps(response.json())

    missing_location = {k: v for k, v in brief_payload.items() if k != "wedding_location"}
    assert client.post("/api/plans", json=missing_location).status_code == 422


def test_missing_keys_return_503(tmp_path, brief_payload):
    settings = PlannerSettings(_env_file=None, groq_api_key="x", db_path=tmp_path / "p.db")
    with TestClient(create_app(settings=settings, planner=FakePlanner())) as client:
        response = client.post("/api/plans", json=brief_payload)
    assert response.status_code == 503
    assert "TAVILY_API_KEY" in response.json()["detail"]


def test_planner_errors_are_mapped(settings, repository, brief_payload):
    class RateLimitError(Exception):
        pass

    cases = [
        (ConfigurationError("no key"), 503),
        (RateLimitError("slow down"), 429),
        (ValueError("boom"), 500),
    ]
    for error, status in cases:
        app = create_app(settings=settings, planner=FakePlanner(error), repository=repository)
        with TestClient(app) as client:
            response = client.post("/api/plans", json=brief_payload)
        assert response.status_code == status, (error, response.text)
    assert repository.count() == 0


def test_stream_emits_progress_then_plan(client, brief_payload):
    with client.stream("POST", "/api/plans/stream", json=brief_payload) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/x-ndjson")
        messages = [json.loads(line) for line in response.iter_lines() if line]

    types = [message["type"] for message in messages]
    assert types[-1] == "plan"
    assert "progress" in types
    stages = [m["event"]["stage"] for m in messages if m["type"] == "progress"]
    assert stages[0] == "planning" and "saving" in stages
    assert client.get("/api/plans").json()["total"] == 1


def test_stream_reports_errors_as_final_message(settings, repository, brief_payload):
    app = create_app(
        settings=settings, planner=FakePlanner(ValueError("kaput")), repository=repository
    )
    with (
        TestClient(app) as client,
        client.stream("POST", "/api/plans/stream", json=brief_payload) as response,
    ):
        messages = [json.loads(line) for line in response.iter_lines() if line]
    assert messages[-1]["type"] == "error"
    assert messages[-1]["status_code"] == 500
    assert "kaput" in messages[-1]["detail"]
