import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GateResult:
    passed: bool
    reliability_at_k: float
    min_reliability: float
    failed_tasks: int
    max_failed_tasks: int
    reasons: list[str]

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "reliability_at_k": round(self.reliability_at_k, 4),
            "min_reliability": self.min_reliability,
            "failed_tasks": self.failed_tasks,
            "max_failed_tasks": self.max_failed_tasks,
            "reasons": self.reasons,
        }


def evaluate_gate(
    input_dir: Path,
    min_reliability: float = 0.8,
    max_failed_tasks: int = 5,
) -> GateResult:
    summary_path = input_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"missing artifact: {summary_path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    reliability_at_k = float(summary.get("reliability_at_k", 0.0))
    failed_tasks = int(summary.get("failed", 0))

    reasons: list[str] = []
    if reliability_at_k < min_reliability:
        reasons.append(
            f"reliability_at_k {reliability_at_k:.4f} below threshold {min_reliability:.4f}"
        )
    if failed_tasks > max_failed_tasks:
        reasons.append(
            f"failed tasks {failed_tasks} exceeds threshold {max_failed_tasks}"
        )

    return GateResult(
        passed=len(reasons) == 0,
        reliability_at_k=reliability_at_k,
        min_reliability=min_reliability,
        failed_tasks=failed_tasks,
        max_failed_tasks=max_failed_tasks,
        reasons=reasons,
    )
