# Agentic Reliability Demo (5–7 min)

## What this demo proves
- We log **all prompts**.
- We log **all tool calls**.
- We log **which model** produced each step.
- We can slice reliability by **skill** and identify weakest areas quickly.

## 1) Start API
```bash
cd backend
uvicorn app.main:app --port 8020
```

## 2) Run demo script
In a second terminal:
```bash
cd demo
bash run_demo.sh
```

## 3) Talking points
- "This is not generic logs. It is reliability telemetry aligned to agent workflow spans."
- "Coverage metrics show if prompt/model instrumentation is complete."
- "Skill-level failure rates drive where we intervene first (prompt policy, tool schema, verifier checks)."
- "Replay queue is wired for deterministic postmortem in P1 worker."
