import csv
import json
from pathlib import Path

from app.ark.report import generate_report


def test_generate_report_outputs_markdown_and_csv(tmp_path: Path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir(parents=True)

    summary = {
        "suite": "core25",
        "model": "openrouter/auto",
        "task_count": 4,
        "passed": 2,
        "failed": 2,
        "reliability_at_k": 0.5,
    }
    (artifacts / "summary.json").write_text(json.dumps(summary), encoding="utf-8")

    trace_rows = [
        {
            "suite": "core25",
            "model": "openrouter/auto",
            "step_id": "t01",
            "event_type": "task_completed",
            "latency_ms": 130,
            "error_type": None,
            "retry_count": 0,
            "final_state": "pass",
        },
        {
            "suite": "core25",
            "model": "openrouter/auto",
            "step_id": "t02",
            "event_type": "task_failed",
            "latency_ms": 170,
            "error_type": "retry_exhaustion",
            "retry_count": 2,
            "final_state": "fail",
        },
        {
            "suite": "core25",
            "model": "openrouter/auto",
            "step_id": "t03",
            "event_type": "task_failed",
            "latency_ms": 180,
            "error_type": "tool_contract_mismatch",
            "retry_count": 1,
            "final_state": "fail",
        },
        {
            "suite": "core25",
            "model": "openrouter/auto",
            "step_id": "t04",
            "event_type": "task_completed",
            "latency_ms": 150,
            "error_type": None,
            "retry_count": 0,
            "final_state": "pass",
        },
    ]
    with (artifacts / "traces.jsonl").open("w", encoding="utf-8") as f:
        for row in trace_rows:
            f.write(json.dumps(row) + "\n")

    out = tmp_path / "reports"
    outputs = generate_report(input_dir=artifacts, output_dir=out)

    md_path = Path(outputs["markdown"])
    csv_path = Path(outputs["csv"])
    assert md_path.exists()
    assert csv_path.exists()

    md = md_path.read_text(encoding="utf-8")
    assert "# Reliability Report" in md
    assert "Reliability@K: **0.5**" in md
    assert "| retry_exhaustion | 1 |" in md
    assert "| tool_contract_mismatch | 1 |" in md
    assert "## Top-3 Fix Suggestions" in md

    with csv_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 4
    assert rows[1]["failure_class"] == "retry_exhaustion"


def test_generate_report_missing_artifact_raises(tmp_path: Path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir(parents=True)
    (artifacts / "summary.json").write_text("{}", encoding="utf-8")

    try:
        generate_report(input_dir=artifacts)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as e:
        assert "traces.jsonl" in str(e)
