# W1-Day1 Reliability Snapshot

Date: 2026-03-10
Project: agentic-reliability-platform
Suite: core25 (25-task canonical pack)

## Executive summary
- Initial ARK runner scaffold is live.
- Local suite execution now emits:
  - `traces.jsonl`
  - `summary.json`
- Current seeded baseline:
  - Task count: 25
  - Passed: 17
  - Failed: 8
  - Reliability@K: 0.68

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
- This is a Day-1 velocity snapshot with the full Core25 pack enabled.
