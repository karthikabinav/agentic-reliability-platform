import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


FIX_SUGGESTIONS: dict[str, str] = {
    "retry_exhaustion": "Tune retry policy per tool (caps/backoff/jitter) and add fallback branches before terminal failure.",
    "tool_contract_mismatch": "Validate tool args against a strict schema before invocation and surface corrective feedback to the planner.",
    "invalid_tool_name": "Enforce tool allowlists and add pre-execution normalization/aliasing for tool names.",
    "context_loss": "Preserve and rehydrate execution state between steps; add checkpoints for long-horizon tasks.",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _failure_counter(traces: list[dict[str, Any]]) -> Counter:
    c: Counter = Counter()
    for row in traces:
        failure = row.get("error_type") or row.get("failure_class")
        if failure:
            c[str(failure)] += 1
    return c


def _top_fix_suggestions(failures: Counter, limit: int = 3) -> list[tuple[str, int, str]]:
    out: list[tuple[str, int, str]] = []
    for failure_class, count in failures.most_common(limit):
        suggestion = FIX_SUGGESTIONS.get(
            failure_class,
            "Review failing traces for this class and add targeted guardrails/tests for detection and recovery.",
        )
        out.append((failure_class, count, suggestion))
    return out


def generate_report(input_dir: Path, output_dir: Path | None = None) -> dict[str, str]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir) if output_dir else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = input_dir / "summary.json"
    traces_path = input_dir / "traces.jsonl"
    if not summary_path.exists():
        raise FileNotFoundError(f"missing required artifact: {summary_path}")
    if not traces_path.exists():
        raise FileNotFoundError(f"missing required artifact: {traces_path}")

    summary = _read_json(summary_path)
    traces = _read_jsonl(traces_path)

    failures = _failure_counter(traces)
    top3 = _top_fix_suggestions(failures, limit=3)

    csv_path = output_dir / "reliability-report.csv"
    fieldnames = [
        "suite",
        "model",
        "step_id",
        "event_type",
        "final_state",
        "failure_class",
        "retry_count",
        "latency_ms",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in traces:
            writer.writerow(
                {
                    "suite": row.get("suite", summary.get("suite", "")),
                    "model": row.get("model", summary.get("model", "")),
                    "step_id": row.get("step_id", ""),
                    "event_type": row.get("event_type", ""),
                    "final_state": row.get("final_state", ""),
                    "failure_class": row.get("error_type", "") or "",
                    "retry_count": row.get("retry_count", ""),
                    "latency_ms": row.get("latency_ms", ""),
                }
            )

    md_path = output_dir / "reliability-report.md"
    failure_rows = [
        f"| {failure_class} | {count} |"
        for failure_class, count in failures.most_common()
    ] or ["| none | 0 |"]

    suggestion_rows = [
        f"{i}. **{failure_class}** ({count}): {suggestion}"
        for i, (failure_class, count, suggestion) in enumerate(top3, start=1)
    ] or ["1. No failures detected; prioritize expanding adversarial coverage to prevent regressions."]

    md = "\n".join(
        [
            "# Reliability Report",
            "",
            "## Summary",
            f"- Suite: `{summary.get('suite', 'unknown')}`",
            f"- Model: `{summary.get('model', 'unknown')}`",
            f"- Tasks: **{summary.get('task_count', len(traces))}**",
            f"- Passed: **{summary.get('passed', 0)}**",
            f"- Failed: **{summary.get('failed', 0)}**",
            f"- Reliability@K: **{summary.get('reliability_at_k', 0)}**",
            "",
            "## Failure Taxonomy",
            "| failure_class | count |",
            "|---|---:|",
            *failure_rows,
            "",
            "## Top-3 Fix Suggestions",
            *suggestion_rows,
            "",
            "## Artifacts",
            f"- Source summary: `{summary_path}`",
            f"- Source traces: `{traces_path}`",
            f"- CSV output: `{csv_path}`",
        ]
    )
    md_path.write_text(md + "\n", encoding="utf-8")

    return {
        "input_dir": str(input_dir),
        "summary": str(summary_path),
        "traces": str(traces_path),
        "markdown": str(md_path),
        "csv": str(csv_path),
    }
