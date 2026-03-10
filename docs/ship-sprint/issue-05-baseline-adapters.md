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
- [ ] Adapters implement shared interface and pass integration smoke tests.
- [ ] Baseline run command documented and reproducible.
- [ ] Example output artifacts included in docs.

## Labels
`integrations`, `help-wanted`
