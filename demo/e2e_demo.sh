#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
DEMO_DIR="$ROOT_DIR/demo"
ARTIFACT_DIR="$BACKEND_DIR/artifacts/core25-baseline"
PORT="8020"
API_URL="http://127.0.0.1:${PORT}/v1/observability/health"

cleanup() {
  if [[ -n "${UVICORN_PID:-}" ]] && kill -0 "$UVICORN_PID" 2>/dev/null; then
    kill "$UVICORN_PID" || true
  fi
}
trap cleanup EXIT

echo "== [1/5] Verifying Python env =="
if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
  echo "Missing backend/.venv. Create it first:"
  echo "  cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -e .[dev]"
  exit 1
fi

# shellcheck source=/dev/null
source "$BACKEND_DIR/.venv/bin/activate"

command -v ark >/dev/null || { echo "ark CLI missing. Run: pip install -e .[dev]"; exit 1; }

echo "== [2/5] Starting API server on :${PORT} =="
cd "$BACKEND_DIR"
uvicorn app.main:app --port "$PORT" >/tmp/agentic_reliability_uvicorn.log 2>&1 &
UVICORN_PID=$!

for _ in {1..30}; do
  if curl -sf "$API_URL" >/dev/null; then
    break
  fi
  sleep 0.5
done
curl -sf "$API_URL" >/dev/null || { echo "API failed to start. See /tmp/agentic_reliability_uvicorn.log"; exit 1; }

echo "== [3/5] Running telemetry ingestion demo =="
cd "$DEMO_DIR"
bash run_demo.sh

echo "== [4/5] Running ARK baseline + report + gate =="
cd "$BACKEND_DIR"
rm -rf "$ARTIFACT_DIR"
ark run --suite core25 --model openrouter:openai/gpt-4o-mini --out "$ARTIFACT_DIR"
ark report --in "$ARTIFACT_DIR" --out "$ARTIFACT_DIR"
ark gate --in "$ARTIFACT_DIR" --min-reliability 0.80 --max-failed-tasks 5

echo "== [5/5] Done =="
echo "Artifacts: $ARTIFACT_DIR"
echo "- traces.jsonl"
echo "- summary.json"
echo "- reliability-report.md"
echo "- reliability-report.csv"
echo "\nSee expected snapshot: $DEMO_DIR/expected_output_ascii.txt"
