import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.main import app


def test_ingest_trace_metrics_and_replay():
    c = TestClient(app)

    payload = {
        "tenant_id": "t_1",
        "events": [
            {
                "trace_id": "tr_1",
                "span_id": "sp_1",
                "workflow_id": "wf_1",
                "agent_id": "agent_a",
                "task_id": "task_1",
                "event_type": "run_started",
                "skill_tag": "repo_navigation",
                "payload": {"x": 1},
            },
            {
                "trace_id": "tr_1",
                "span_id": "sp_1p",
                "parent_span_id": "sp_1",
                "workflow_id": "wf_1",
                "agent_id": "agent_a",
                "task_id": "task_1",
                "event_type": "prompt_logged",
                "skill_tag": "code_generation",
                "model_version": "claude-4.5",
                "payload": {"prompt": "Write a function"},
            },
            {
                "trace_id": "tr_1",
                "span_id": "sp_2",
                "parent_span_id": "sp_1",
                "workflow_id": "wf_1",
                "agent_id": "agent_a",
                "task_id": "task_1",
                "event_type": "tool_call_started",
                "skill_tag": "debugging",
                "model_version": "claude-4.5",
                "failure_class": "tool_contract_mismatch",
                "payload": {"tool_name": "search", "tool_input": {"q": "traceback"}},
            },
        ],
    }

    r = c.post("/v1/observability/events", json=payload)
    assert r.status_code == 200
    assert r.json()["accepted"] == 3

    tr = c.get("/v1/observability/traces/tr_1")
    assert tr.status_code == 200
    assert len(tr.json()["events"]) >= 2

    m = c.get("/v1/observability/metrics", params={"tenant_id": "t_1"})
    assert m.status_code == 200
    assert m.json()["totals"]["events"] >= 2

    s = c.get("/v1/observability/search", params={"tenant_id": "t_1", "skill_tag": "debugging"})
    assert s.status_code == 200
    assert s.json()["count"] >= 1

    sm = c.get("/v1/observability/metrics/skills", params={"tenant_id": "t_1"})
    assert sm.status_code == 200
    assert len(sm.json()["skills"]) >= 1

    s2 = c.get("/v1/observability/search", params={"tenant_id": "t_1", "has_prompt": True})
    assert s2.status_code == 200
    assert s2.json()["count"] >= 1

    bad = c.post(
        "/v1/observability/events",
        json={
            "tenant_id": "t_1",
            "events": [
                {
                    "trace_id": "tr_bad",
                    "span_id": "sp_bad",
                    "workflow_id": "wf_1",
                    "agent_id": "agent_a",
                    "task_id": "task_bad",
                    "event_type": "tool_call_started",
                    "payload": {"tool_name": "search"}
                }
            ],
        },
    )
    assert bad.status_code == 200
    assert bad.json()["accepted"] == 0
    assert bad.json()["rejected"] == 1

    rep = c.post("/v1/observability/replay", json={"trace_id": "tr_1", "mode": "deterministic"})
    assert rep.status_code == 200
    replay_id = rep.json()["replay_id"]

    rs = c.get(f"/v1/observability/replay/{replay_id}")
    assert rs.status_code == 200
    assert rs.json()["status"] == "queued"
