# Issue #3 — Trace schema v0 + event emitters

## Title
Define trace schema v0 and emit required reliability fields

## Why
Reliability analysis is blocked without standardized per-step telemetry.

## Scope
- Define schema fields:
  - `step_id`
  - `tool_call`
  - `latency_ms`
  - `error_type`
  - `retry_count`
  - `final_state`
- Include required envelope fields: `ts`, `suite`, `model`, `event_type`.
- Add schema validation tests.
- Ensure runner emits schema-compliant records.

## Implementation (v0)
- JSON schema path: `backend/app/ark/schemas/trace.schema.v0.json`
- Emitted artifact path: `<out>/traces.jsonl` from `ark run ...`
- Validation test: `backend/tests/test_ark_trace_schema.py`

### Field mapping (runner internals → trace schema)
- `task.id` → `step_id`
- `task.category` (or optional `task.tool_call`) → `tool_call`
- simulated latency value → `latency_ms`
- failure class (`retry_exhaustion` or `null`) → `error_type`
- pass/fail-derived retry budget (`0`/`2`) → `retry_count`
- pass/fail result → `final_state` (`pass`/`fail`)
- run metadata timestamp → `ts`
- selected suite name → `suite`
- CLI model arg → `model`
- pass/fail event → `event_type` (`task_completed`/`task_failed`)

## Usage
```bash
ark run --suite core25 --model openrouter/auto --out ./artifacts/core25
pytest backend/tests/test_ark_cli.py backend/tests/test_ark_trace_schema.py
```

## Acceptance criteria
- [ ] JSON schema file added and versioned.
- [ ] Emitter output validates against schema in tests.
- [ ] Clear mapping doc from internal events -> schema fields.

## Labels
`observability`, `core`
