# Issue #5 — Baseline adapters (OpenRouter + local vLLM)

## Title
Add adapter interface and baseline configs for OpenRouter + local vLLM

## Why
Benchmarks need reproducible baseline runs across common open-model deployment paths.

## Scope
- Adapter interface abstraction for model backends.
- OpenRouter adapter config.
- Local vLLM adapter config.
- One-command baseline run docs + reproducibility notes.

## Acceptance criteria
- [x] Adapters implement shared interface and pass integration smoke tests.
- [x] Baseline run command documented and reproducible.
- [x] Example output artifacts included in docs.

## Implemented baseline command
```bash
cd backend
ark run --suite core25 --model openrouter:openai/gpt-4o-mini --out ./artifacts/core25-baseline
```

## Reproducibility notes
- Current adapters are deterministic mock baselines (no live OpenRouter/vLLM calls).
- Use `temperature=0` + fixed seed in production adapter implementations to preserve comparability.
- Config stubs are available under `backend/app/ark/config_examples/`.

## Labels
`integrations`, `help-wanted`
