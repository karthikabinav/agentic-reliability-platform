import json
from pathlib import Path

from app.ark.cli import run


def test_ark_run_writes_summary_and_traces(tmp_path: Path):
    out = tmp_path / "artifacts"
    summary = run(suite="core25", model="openrouter/auto", out=out)

    assert summary["suite"] == "core25"
    assert summary["task_count"] == 5
    assert (out / "summary.json").exists()
    assert (out / "traces.jsonl").exists()

    parsed = json.loads((out / "summary.json").read_text())
    assert parsed["passed"] + parsed["failed"] == 5
