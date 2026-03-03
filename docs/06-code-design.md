# Agentic Reliability Platform — Code Design (MVP)

This document describes the **current backend implementation** in `backend/app/*` so code review can be done line-by-line against architecture and behavior.

---

## 1) System shape

**Stack**
- FastAPI (HTTP API)
- SQLAlchemy ORM (persistence)
- SQLite default storage (`agentic_reliability.db`)

**Primary objective**
- Ingest agent observability events
- Enforce minimal telemetry contract for prompt/tool/model coverage
- Provide search, trace drill-down, aggregate metrics, skill-level reliability slices
- Queue replay jobs (stub lifecycle for P1 worker)

---

## 2) Module map

### `app/main.py`
- Creates FastAPI app (`title="Agentic Reliability MVP"`, `version="0.1.0"`)
- Mounts router from `app.api.routes`
- Startup hook calls `init_db()` to ensure tables exist.

### `app/core/config.py`
- Defines `Settings` with one field: `database_url`
- Default: `sqlite:///./agentic_reliability.db`

### `app/db/base.py`
- SQLAlchemy declarative base (`class Base(DeclarativeBase)`)

### `app/db/session.py`
- Creates SQLAlchemy engine from settings
- Adds sqlite `check_same_thread=False` for local use
- Exposes:
  - `init_db()` → `Base.metadata.create_all(bind=engine)`
  - `get_db()` dependency (yield session + close in finally)

### `app/db/models.py`
- `ObsEvent` table: atomic event telemetry row
- `ReplayJob` table: async replay request lifecycle state

### `app/services/schemas.py`
- Pydantic request/response models:
  - `EventIn`, `IngestRequest`, `IngestResponse`, `ReplayRequest`
- Includes guidance comment on required payload/model fields for prompt and tool events.

### `app/api/routes.py`
- All HTTP routes under `/v1/observability`
- Implements ingestion, query/search, metrics, and replay APIs.

---

## 3) Data model details

## `ObsEvent`
Event grain = one row per event emitted by an agent workflow.

Key columns:
- Tenant/workflow identity: `tenant_id`, `workflow_id`, `agent_id`, `task_id`
- Trace structure: `trace_id`, `span_id`, `parent_span_id`
- Semantics: `event_type`, `skill_tag`, `failure_class`
- Payload: `payload` (JSON)
- Versioning: `policy_version`, `model_version`
- Time: `ts`

Design intent:
- Supports distributed trace reconstruction (`trace_id/span_id/parent_span_id`)
- Supports both reliability and capability diagnostics via `failure_class + skill_tag`
- Supports model-attribution by event via `model_version`

## `ReplayJob`
- `replay_id` external identifier
- `trace_id` replay target
- `mode`, target versions, status/result payload
- Currently starts as `status="queued"`; execution pipeline is intentionally deferred.

---

## 4) API behavior by endpoint

## `GET /health`
Returns `{"ok": true}`.

## `POST /events`
Batch ingest endpoint (`IngestRequest`).

Validation/enforcement (important):
- If `event_type == "prompt_logged"`:
  - requires `payload.prompt`
  - requires `model_version`
- If `event_type in {"tool_call_started", "tool_call_finished"}`:
  - requires `payload.tool_name`
  - requires `model_version`

Error handling:
- Per-event try/except, so batch is partially accepted.
- Output includes accepted/rejected counts and indexed error strings (`event[i] rejected: ...`).

Commit model:
- Adds all accepted rows, then commits once per request.

## `GET /traces/{trace_id}`
- Fetches all events for trace ordered ascending by timestamp.
- Returns canonical event projection including `payload`, `skill_tag`, `model_version`.

## `GET /search`
Filters:
- SQL-level: `tenant_id` (required), optional `workflow_id`, `event_type`, `skill_tag`, `failure_class`, `model_version`
- App-level payload filters: `tool_name`, `has_prompt`

Implementation detail:
- Pulls up to `max(limit*5, 200)` rows from DB first to allow payload-level filtering in memory.
- Returns normalized compact item shape including:
  - `tool_name` extracted from payload
  - `has_prompt` boolean derived from payload

## `GET /metrics`
Returns tenant/workflow aggregate counters and rates:
- totals: `events`, `failures`, `escalations`, `tool_calls`, `prompt_events`, `modeled_events`
- rates: `failure_rate`, `escalation_rate`, `prompt_coverage_rate`, `model_coverage_rate`

Interpretation:
- `prompt_coverage_rate` and `model_coverage_rate` are instrumentation completeness checks.

## `GET /metrics/skills`
- Groups by `skill_tag`
- Computes total events + failures + failure rate per skill
- Null skill tag mapped to `"unlabeled"` in response
- Sorted by event volume descending

## `POST /replay`
- Creates replay row with generated `replay_id = rp_<10 hex chars>`
- Status set to `queued`; result is MVP stub note.

## `GET /replay/{replay_id}`
- Returns replay state if exists, else `{ "error": "not_found" }`.

---

## 5) End-to-end flow

1. Client emits event batch to `/events`.
2. API validates prompt/tool/model contract and stores accepted events.
3. Operator uses:
   - `/traces/{trace_id}` for forensic timeline
   - `/search` for targeted slices (skill/model/tool/prompt)
   - `/metrics` for top-line reliability + coverage
   - `/metrics/skills` for intervention prioritization
4. Operator can queue replay with `/replay` for later deterministic rerun machinery.

---

## 6) Current limitations (intentional MVP scope)

- No auth/tenant isolation hardening yet.
- No migration framework (table creation uses `create_all`).
- Payload-level filters run in app memory, not SQL JSON path indices.
- No replay executor/worker yet (queue stub only).
- No retention/compression strategy yet for high-volume telemetry.

---

## 7) Verification checklist

To verify implementation quickly against code:
- Enforcement logic: `app/api/routes.py::ingest_events`
- Coverage metrics math: `app/api/routes.py::metrics`
- Skill aggregation query: `app/api/routes.py::skill_metrics`
- Data model columns: `app/db/models.py::ObsEvent`
- Startup table creation: `app/main.py` + `app/db/session.py::init_db`
