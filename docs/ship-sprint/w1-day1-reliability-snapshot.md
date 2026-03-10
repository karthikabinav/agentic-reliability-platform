# W1-Day1 Reliability Snapshot

Date: 2026-03-10
Project: agentic-reliability-platform
Suite: core25 (initial scaffold subset currently 5 tasks)

## Executive summary
- Initial ARK runner scaffold is live.
- Local suite execution now emits:
  - `traces.jsonl`
  - `summary.json`
- Current seeded baseline (scaffold subset):
  - Task count: 5
  - Passed: 3
  - Failed: 2
  - Reliability@K: 0.60

## Top observed failure modes (seeded in scaffold)
- retry_exhaustion
- hallucinated/invalid tool selection (covered by adversarial case)
- constrained recovery path failures

## Mitigation PRs queued next
1. Add richer failure taxonomy (`tool_contract_mismatch`, `invalid_tool_name`, `context_loss`, `retry_exhaustion`).
2. Add retry policy profiles with per-tool caps/backoff to improve constrained recovery.
3. Add tool-allowlist validator + argument schema checks before execution.

## Reproduce
```bash
cd backend
python -m app.ark.cli run --suite core25 --model openrouter:openai/gpt-4o-mini --out ./artifacts/core25-baseline
cat ./artifacts/core25-baseline/summary.json
```

## Notes
- This is a Day-1 scaffold snapshot for velocity.
- Core25 will be expanded from 5 -> 25 canonical tasks in Week 1.
