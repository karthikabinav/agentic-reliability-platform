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
- Add schema validation tests.
- Ensure runner emits schema-compliant records.

## Acceptance criteria
- [ ] JSON schema file added and versioned.
- [ ] Emitter output validates against schema in tests.
- [ ] Clear mapping doc from internal events -> schema fields.

## Labels
`observability`, `core`
