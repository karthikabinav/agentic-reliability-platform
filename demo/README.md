# Agentic Reliability Demo

## Fast path (<10 min)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

cd ../demo
bash e2e_demo.sh
```

This runs:
1. API startup (`uvicorn` on `:8020`)
2. Telemetry ingest + search + metrics (`run_demo.sh`)
3. ARK run + report + release gate

Expected snapshot: `expected_output_ascii.txt`
Mock screenshot: `sample_screenshot_mock.html`

## Manual path
### 1) Start API
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --port 8020
```

### 2) Run telemetry script
```bash
cd demo
bash run_demo.sh
```

### 3) Run ARK CLI
```bash
cd ../backend
ark run --suite core25 --model openrouter:openai/gpt-4o-mini --out ./artifacts/core25-baseline
ark report --in ./artifacts/core25-baseline --out ./artifacts/core25-baseline
ark gate --in ./artifacts/core25-baseline --min-reliability 0.80 --max-failed-tasks 5
```
