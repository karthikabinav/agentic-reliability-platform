# Agentic Reliability MVP Backend

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8020
```

## API
- `GET /v1/observability/health`
- `POST /v1/observability/events`
- `GET /v1/observability/traces/{trace_id}`
- `GET /v1/observability/search` (supports `skill_tag` filter)
- `GET /v1/observability/metrics`
- `GET /v1/observability/metrics/skills`
- `POST /v1/observability/replay`
- `GET /v1/observability/replay/{replay_id}`

## Demo
- Quick showcase: `../demo/README.md`
- Script: `../demo/run_demo.sh`

## ARK Runner (new)
One-command reproducible baseline run:
```bash
ark run --suite core25 --model openrouter:openai/gpt-4o-mini --out ./artifacts/core25-baseline
```

Also supported:
- `--model vllm:meta-llama/Llama-3.1-8B-Instruct`
- legacy format `--model openrouter/auto`

Outputs:
- `traces.jsonl` (step-level telemetry)
- `summary.json` (Reliability@K summary)

Reproducibility notes:
- Baseline adapters are deterministic stubs (mocked, no network calls).
- Task outcomes are seeded by `(backend, model_name, task_id)`.
- Example backend configs live in:
  - `app/ark/config_examples/openrouter.example.json`
  - `app/ark/config_examples/vllm.example.json`

Generate reliability reports from artifacts:
```bash
ark report --in ./artifacts/core25 --out ./artifacts/core25
```
Outputs:
- `reliability-report.md` (summary + failure taxonomy + top-3 fixes)
- `reliability-report.csv` (analysis-friendly per-task rows)

Trace schema v0:
- Schema file: `backend/app/ark/schemas/trace.schema.v0.json`
- Each `traces.jsonl` row includes: `ts`, `suite`, `model`, `step_id`, `tool_call`, `event_type`, `latency_ms`, `error_type`, `retry_count`, `final_state`.
- Validation test: `pytest backend/tests/test_ark_trace_schema.py`

## Notes
- SQLite default for MVP.
- Replay endpoint is a queued stub in P0 (real worker in P1).
- Observability contract (MVP):
  - `prompt_logged` events must include `payload.prompt` and `model_version`.
  - `tool_call_started` / `tool_call_finished` must include `payload.tool_name` and `model_version`.
