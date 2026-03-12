# Agentic Reliability Platform

**Reliability telemetry + release gating for agent workflows.**

## Launch (concise)

### Problem
Agent teams are shipping faster than their reliability controls. Most teams can’t answer:
- Which skills/workflows are failing most?
- Are prompts/tool-calls/model versions fully logged for postmortems?
- Should this model/prompt change be blocked from release?

### Solution
This repo provides a minimal but usable reliability stack:
- **Observability API** for prompt/tool/model telemetry
- **ARK CLI** for reproducible benchmark runs (`ark run`)
- **Report + Gate** to turn traces into release decisions (`ark report`, `ark gate`)

### Why now
Agentic systems now touch production workflows. Reliability has to be **measured and enforced** (not reviewed ad hoc after failures).

### What you can test immediately
In under 10 minutes you can:
1. Run a full local e2e demo.
2. Ingest realistic coding-agent telemetry.
3. Generate skill-level reliability metrics.
4. Run a release gate that passes/fails on Reliability@K thresholds.

---

## Quickstart demo (<10 min)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

cd ../demo
bash e2e_demo.sh
```

What this script does:
- Starts API on `http://127.0.0.1:8020`
- Runs telemetry ingestion (`demo/run_demo.sh`)
- Runs ARK baseline + report + gate
- Prints artifact locations + expected output snapshot

Expected output snapshot: `demo/expected_output_ascii.txt`

---

## Demo path (manual)

### 1) Start API
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --port 8020
```

### 2) In another shell, run telemetry demo
```bash
cd demo
bash run_demo.sh
```

### 3) Run ARK benchmark + gate
```bash
cd ../backend
ark run --suite core25 --model openrouter:openai/gpt-4o-mini --out ./artifacts/core25-baseline
ark report --in ./artifacts/core25-baseline --out ./artifacts/core25-baseline
ark gate --in ./artifacts/core25-baseline --min-reliability 0.80 --max-failed-tasks 5
```

---

## Install as an OpenClaw skill

This repo includes a portable skill package at:
- `openclaw-skill/agentic-reliability/`

### Skill folder structure
```text
openclaw-skill/
  agentic-reliability/
    SKILL.md
    _meta.json
```

### Option A: Local install (workspace)
```bash
mkdir -p ~/.openclaw/workspace/skills/agentic-reliability
cp -r openclaw-skill/agentic-reliability/* ~/.openclaw/workspace/skills/agentic-reliability/
```

### Option B: ClawHub-style packaging notes
- Keep `SKILL.md` + `_meta.json` at package root.
- Use concise, executable commands in `SKILL.md`.
- Reference repo-local scripts (`demo/e2e_demo.sh`) for deterministic runs.
- Include sample outputs so skill users can verify success quickly.

### Use from OpenClaw
Ask your agent:
- “Run the agentic reliability e2e demo in this repo.”
- “Generate a reliability report from `backend/artifacts/core25-baseline`.”
- “Run release gate with min reliability 0.85.”

---

## Repo map
- `backend/` — FastAPI service + ARK CLI
- `demo/` — demo scripts + expected output + screenshot mock
- `openclaw-skill/agentic-reliability/` — installable skill package
- `docs/` — architecture and implementation notes

## Screenshots / snapshots
- Mock UI screenshot: `demo/sample_screenshot_mock.html`
- ASCII run snapshot: `demo/expected_output_ascii.txt`

## Status
MVP but publicly demoable. Focused on practical reliability loops: **instrument -> measure -> report -> gate**.
