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

## Notes
- SQLite default for MVP.
- Replay endpoint is a queued stub in P0 (real worker in P1).
- Observability contract (MVP):
  - `prompt_logged` events must include `payload.prompt` and `model_version`.
  - `tool_call_started` / `tool_call_finished` must include `payload.tool_name` and `model_version`.
