import json
from pathlib import Path

from app.ark.cli import run
from app.ark.gate import evaluate_gate


def test_gate_passes_with_default_thresholds(tmp_path: Path):
    out = tmp_path / "artifacts"
    run(suite="core25", model="openrouter/auto", out=out)

    result = evaluate_gate(input_dir=out)

    assert result.passed is True
    assert result.failed_tasks <= result.max_failed_tasks
    assert result.reliability_at_k >= result.min_reliability


def test_gate_fails_with_strict_threshold(tmp_path: Path):
    out = tmp_path / "artifacts"
    run(suite="core25", model="openrouter/auto", out=out)

    result = evaluate_gate(input_dir=out, min_reliability=0.99)

    assert result.passed is False
    assert any("below threshold" in reason for reason in result.reasons)

    payload = result.to_dict()
    assert isinstance(payload["reasons"], list)
    assert json.loads(json.dumps(payload))["passed"] is False
