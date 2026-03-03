# Concrete Use Case: Monitor My Coding Agent by Skill

## Use case
Track reliability of a coding agent where each event is tagged by skill area:
- `repo_navigation`
- `code_generation`
- `debugging`
- `test_fixing`
- `tool_use`

## Why this matters
A single aggregate failure rate hides where the agent is weak. Skill-level observability shows where to intervene first.

## Data convention
Every ingested event should include `skill_tag`.

Example event:
```json
{
  "trace_id": "tr_123",
  "span_id": "sp_2",
  "workflow_id": "coding_assistant",
  "agent_id": "coder_v1",
  "task_id": "task_99",
  "event_type": "tool_call_finished",
  "skill_tag": "debugging",
  "failure_class": null,
  "payload": {"tool": "pytest"}
}
```

## API flow
1. Ingest events with skill tags:
   - `POST /v1/observability/events`
2. Query failure-heavy slices:
   - `GET /v1/observability/search?tenant_id=t_1&skill_tag=debugging`
3. View skill-level reliability:
   - `GET /v1/observability/metrics/skills?tenant_id=t_1`

## Expected MVP value
- identify weakest skills quickly
- prioritize prompt/tool/policy improvements by skill
- quantify whether each intervention improves reliability
