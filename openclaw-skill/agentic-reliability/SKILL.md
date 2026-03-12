# Agentic Reliability (OpenClaw Skill)

Run a fast local reliability demo for the Agentic Reliability Platform.

## When to use
- User asks to demo agent reliability instrumentation quickly.
- User asks for reliability report generation from ARK artifacts.
- User asks for release gate checks (Reliability@K thresholding).

## Inputs
- Optional artifact directory (default: `backend/artifacts/core25-baseline`)
- Optional gate thresholds (`min_reliability`, `max_failed_tasks`)

## Commands
### End-to-end local demo (<10 min)
```bash
cd /path/to/agentic-reliability-platform
bash demo/e2e_demo.sh
```

### Report only
```bash
cd /path/to/agentic-reliability-platform/backend
ark report --in ./artifacts/core25-baseline --out ./artifacts/core25-baseline
```

### Gate only
```bash
cd /path/to/agentic-reliability-platform/backend
ark gate --in ./artifacts/core25-baseline --min-reliability 0.80 --max-failed-tasks 5
```

## Success checks
- `traces.jsonl` and `summary.json` exist in artifact folder.
- `reliability-report.md` generated.
- Gate command exits `0` for pass.
