#!/usr/bin/env bash
set -euo pipefail

BASE="http://127.0.0.1:8020/v1/observability"
TENANT="demo_tenant"
TRACE="trace_demo_001"

echo "== Health =="
curl -s "$BASE/health"; echo

echo "== Ingesting realistic coding-agent telemetry =="
curl -s -X POST "$BASE/events" \
  -H 'content-type: application/json' \
  -d @- <<JSON
{
  "tenant_id": "$TENANT",
  "events": [
    {
      "trace_id": "$TRACE",
      "span_id": "sp_1",
      "workflow_id": "coding_agent",
      "agent_id": "coder_v1",
      "task_id": "task_bugfix_42",
      "event_type": "prompt_logged",
      "skill_tag": "debugging",
      "model_version": "gpt-5.3-codex",
      "payload": {
        "prompt": "Investigate failing test in parser.py and suggest minimal patch."
      }
    },
    {
      "trace_id": "$TRACE",
      "span_id": "sp_2",
      "parent_span_id": "sp_1",
      "workflow_id": "coding_agent",
      "agent_id": "coder_v1",
      "task_id": "task_bugfix_42",
      "event_type": "tool_call_started",
      "skill_tag": "debugging",
      "model_version": "gpt-5.3-codex",
      "payload": {
        "tool_name": "pytest",
        "tool_input": {"args": "tests/test_parser.py::test_edge_case"}
      }
    },
    {
      "trace_id": "$TRACE",
      "span_id": "sp_3",
      "parent_span_id": "sp_1",
      "workflow_id": "coding_agent",
      "agent_id": "coder_v1",
      "task_id": "task_bugfix_42",
      "event_type": "tool_call_finished",
      "skill_tag": "debugging",
      "model_version": "gpt-5.3-codex",
      "failure_class": "tool_contract_mismatch",
      "payload": {
        "tool_name": "pytest",
        "tool_output": "unexpected flag --json"
      }
    },
    {
      "trace_id": "$TRACE",
      "span_id": "sp_4",
      "parent_span_id": "sp_1",
      "workflow_id": "coding_agent",
      "agent_id": "coder_v1",
      "task_id": "task_bugfix_42",
      "event_type": "prompt_logged",
      "skill_tag": "code_generation",
      "model_version": "gpt-5.3-codex",
      "payload": {
        "prompt": "Write a minimal patch for parser.py and add one regression test."
      }
    }
  ]
}
JSON

echo; echo "== Trace view =="
curl -s "$BASE/traces/$TRACE"; echo

echo "== Skill slice (debugging) =="
curl -s "$BASE/search?tenant_id=$TENANT&skill_tag=debugging"; echo

echo "== Tool slice (pytest) =="
curl -s "$BASE/search?tenant_id=$TENANT&tool_name=pytest"; echo

echo "== Prompt coverage check =="
curl -s "$BASE/search?tenant_id=$TENANT&has_prompt=true"; echo

echo "== Tenant metrics (includes prompt/model coverage rates) =="
curl -s "$BASE/metrics?tenant_id=$TENANT"; echo

echo "== Skill metrics =="
curl -s "$BASE/metrics/skills?tenant_id=$TENANT"; echo

echo "\nDemo complete."
