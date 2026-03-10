import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path



@dataclass
class TaskResult:
    task_id: str
    event_type: str
    failure_class: str | None
    passed: bool
    latency_ms: int


def _load_suite(suite: str) -> dict:
    task_file = Path(__file__).parent / "tasks" / f"{suite}.json"
    if not task_file.exists():
        raise FileNotFoundError(f"suite not found: {task_file}")
    return json.loads(task_file.read_text())


def _simulate_task(task: dict, model: str) -> TaskResult:
    seed = hashlib.sha256(f"{model}:{task['id']}".encode()).hexdigest()
    latency_ms = 100 + int(seed[:2], 16)
    expected = task.get("expected", "pass")
    passed = expected == "pass"
    failure_class = None if passed else "retry_exhaustion"
    return TaskResult(
        task_id=task["id"],
        event_type="task_completed" if passed else "task_failed",
        failure_class=failure_class,
        passed=passed,
        latency_ms=latency_ms,
    )


def run(suite: str, model: str, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    suite_cfg = _load_suite(suite)
    ts = datetime.now(timezone.utc).isoformat()

    results = [_simulate_task(task, model=model) for task in suite_cfg.get("tasks", [])]

    traces_path = out / "traces.jsonl"
    with traces_path.open("w", encoding="utf-8") as f:
        for r in results:
            row = {
                "ts": ts,
                "suite": suite,
                "model": model,
                "step_id": r.task_id,
                "event_type": r.event_type,
                "latency_ms": r.latency_ms,
                "error_type": r.failure_class,
                "retry_count": 0 if r.passed else 2,
                "final_state": "pass" if r.passed else "fail",
            }
            f.write(json.dumps(row) + "\n")

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    reliability_at_k = passed / len(results) if results else 0.0

    summary = {
        "suite": suite,
        "model": model,
        "task_count": len(results),
        "passed": passed,
        "failed": failed,
        "reliability_at_k": round(reliability_at_k, 4),
        "artifacts": {
            "traces": str(traces_path),
            "summary": str(out / "summary.json"),
        },
    }

    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="Agent Reliability Kit runner")
    sub = p.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run a benchmark suite")
    run_p.add_argument("--suite", required=True, default="core25")
    run_p.add_argument("--model", required=True)
    run_p.add_argument("--out", default="./artifacts")

    args = p.parse_args()

    if args.command == "run":
        summary = run(suite=args.suite, model=args.model, out=Path(args.out))
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
