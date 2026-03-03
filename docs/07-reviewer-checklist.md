# Agentic Reliability MVP — Reviewer Checklist (Diff-Style)

Use this to verify implementation quickly. Each check maps to a specific file/function and expected behavior.

---

## A) Boot and DB wiring

- [ ] **App boots and initializes DB tables on startup**
  - File: `backend/app/main.py`
  - Verify: startup event calls `init_db()`.

- [ ] **Engine/session configured from settings**
  - File: `backend/app/db/session.py`
  - Verify: `create_engine(settings.database_url, ...)`, `SessionLocal`, `get_db()` dependency.

- [ ] **SQLite compatibility flag present**
  - File: `backend/app/db/session.py`
  - Verify: `check_same_thread=False` when URL starts with `sqlite`.

---

## B) Data model integrity

- [ ] **Observability table has tracing fields**
  - File: `backend/app/db/models.py` (`ObsEvent`)
  - Verify columns: `trace_id`, `span_id`, `parent_span_id`.

- [ ] **Event table tracks skill + model**
  - File: `backend/app/db/models.py` (`ObsEvent`)
  - Verify columns: `skill_tag`, `model_version`.

- [ ] **Event payload is JSON**
  - File: `backend/app/db/models.py`
  - Verify: `payload` column uses `JSON` with default dict.

- [ ] **Replay table exists with status/result**
  - File: `backend/app/db/models.py` (`ReplayJob`)
  - Verify columns: `replay_id`, `status`, `result`, target versions.

---

## C) Ingestion contract enforcement

- [ ] **Prompt logging contract enforced**
  - File: `backend/app/api/routes.py` (`ingest_events`)
  - Verify rule: `event_type == "prompt_logged"` requires `payload.prompt` and `model_version`.

- [ ] **Tool call contract enforced**
  - File: `backend/app/api/routes.py` (`ingest_events`)
  - Verify rule: `tool_call_started`/`tool_call_finished` require `payload.tool_name` and `model_version`.

- [ ] **Partial batch acceptance implemented**
  - File: `backend/app/api/routes.py` (`ingest_events`)
  - Verify: per-event `try/except`, error accumulation, single commit at end.

---

## D) Query and trace behavior

- [ ] **Trace endpoint returns ordered timeline**
  - File: `backend/app/api/routes.py` (`trace`)
  - Verify query orders by `ObsEvent.ts.asc()`.

- [ ] **Search supports model + skill filters**
  - File: `backend/app/api/routes.py` (`search`)
  - Verify params: `skill_tag`, `model_version`, `failure_class`, `event_type`, `workflow_id`.

- [ ] **Search supports payload-derived filters**
  - File: `backend/app/api/routes.py` (`search`)
  - Verify params: `tool_name`, `has_prompt`, with in-memory filtering.

- [ ] **Search response exposes tool/prompt/model indicators**
  - File: `backend/app/api/routes.py` (`search`)
  - Verify response includes `tool_name`, `has_prompt`, `model_version`.

---

## E) Metrics correctness

- [ ] **Global totals include coverage counters**
  - File: `backend/app/api/routes.py` (`metrics`)
  - Verify totals include: `prompt_events`, `modeled_events`.

- [ ] **Coverage rates computed safely**
  - File: `backend/app/api/routes.py` (`metrics`)
  - Verify: `prompt_coverage_rate`, `model_coverage_rate` handle zero totals.

- [ ] **Skill-level failure aggregation exists**
  - File: `backend/app/api/routes.py` (`skill_metrics`)
  - Verify: `group_by(ObsEvent.skill_tag)` and failure count via SQL `case`.

---

## F) Replay lifecycle stub

- [ ] **Replay submit creates queued job**
  - File: `backend/app/api/routes.py` (`submit_replay`)
  - Verify generated `replay_id`, status `queued`, stub result note.

- [ ] **Replay status endpoint resolves by replay_id**
  - File: `backend/app/api/routes.py` (`replay_status`)
  - Verify not-found returns `{ "error": "not_found" }`.

---

## G) Tests and docs alignment

- [ ] **Test covers prompt/tool/model happy path and reject path**
  - File: `backend/tests/test_mvp.py`
  - Verify:
    - accepted events include `prompt_logged` + `tool_call_started`
    - rejected event when tool event omits required `model_version`

- [ ] **README states observability contract**
  - File: `backend/README.md`
  - Verify contract bullets match route enforcement.

---

## 10-minute smoke script (manual)

1. Start API (`uvicorn app.main:app --port 8020`).
2. POST one valid `prompt_logged` event (expect accepted=1).
3. POST one invalid `tool_call_started` missing model_version (expect rejected=1).
4. GET `/metrics` and confirm `prompt_events >= 1`, `model_coverage_rate > 0`.
5. GET `/search?tool_name=...` and verify tool filter.
6. POST `/replay`, then GET replay status.
