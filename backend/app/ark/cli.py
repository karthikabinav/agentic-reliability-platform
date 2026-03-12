import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.ark.adapters import get_adapter
from app.ark.gate import evaluate_gate
from app.ark.report import generate_report


@dataclass
class TaskResult:
    task_id: str
    event_type: str
    tool_call: str
    failure_class: str | None
    passed: bool
    latency_ms: int
    backend: str
    model_name: str


def _load_suite(suite: str) -> dict:
    task_file = Path(__file__).parent / "tasks" / f"{suite}.json"
    if not task_file.exists():
        raise FileNotFoundError(f"suite not found: {task_file}")
    return json.loads(task_file.read_text())


def _simulate_task(task: dict, model: str) -> TaskResult:
    adapter = get_adapter(model)
    adapter_result = adapter.evaluate_task(task)

    category = task.get("category", "generic")
    tool_call = task.get("tool_call", f"{category}.simulated")

    return TaskResult(
        task_id=task["id"],
        event_type="task_completed" if adapter_result.passed else "task_failed",
        tool_call=tool_call,
        failure_class=adapter_result.failure_class,
        passed=adapter_result.passed,
        latency_ms=adapter_result.latency_ms,
        backend=adapter_result.backend,
        model_name=adapter_result.model_name,
    )


def run(suite: str, model: str, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    suite_cfg = _load_suite(suite)
    ts = datetime.now(timezone.utc).isoformat()

    results = [_simulate_task(task, model=model) for task in suite_cfg.get("tasks", [])]
    backend = results[0].backend if results else "unknown"
    model_name = results[0].model_name if results else model

    traces_path = out / "traces.jsonl"
    with traces_path.open("w", encoding="utf-8") as f:
        for r in results:
            row = {
                "ts": ts,
                "suite": suite,
                "model": model,
                "step_id": r.task_id,
                "tool_call": r.tool_call,
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
        "backend": backend,
        "model_name": model_name,
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
    run_p.add_argument("--model", required=True, help="Model backend spec, e.g. openrouter:openai/gpt-4o-mini or vllm:meta-llama/Llama-3.1-8B-Instruct")
    run_p.add_argument("--out", default="./artifacts")

    report_p = sub.add_parser("report", help="Generate reliability markdown/csv report from artifacts")
    report_p.add_argument("--in", dest="input_dir", required=True, help="Artifact directory containing summary.json + traces.jsonl")
    report_p.add_argument("--out", dest="output_dir", default=None, help="Output directory for report files (defaults to --in)")

    gate_p = sub.add_parser("gate", help="Evaluate release gate from artifacts")
    gate_p.add_argument("--in", dest="input_dir", required=True, help="Artifact directory containing summary.json")
    gate_p.add_argument("--min-reliability", type=float, default=0.8, help="Minimum required Reliability@K")
    gate_p.add_argument("--max-failed-tasks", type=int, default=5, help="Maximum allowed failed tasks")

    args = p.parse_args()

    if args.command == "run":
        summary = run(suite=args.suite, model=args.model, out=Path(args.out))
        print(json.dumps(summary, indent=2))
    elif args.command == "report":
        outputs = generate_report(input_dir=Path(args.input_dir), output_dir=Path(args.output_dir) if args.output_dir else None)
        print(json.dumps(outputs, indent=2))
    elif args.command == "gate":
        result = evaluate_gate(
            input_dir=Path(args.input_dir),
            min_reliability=args.min_reliability,
            max_failed_tasks=args.max_failed_tasks,
        )
        print(json.dumps(result.to_dict(), indent=2))
        raise SystemExit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
