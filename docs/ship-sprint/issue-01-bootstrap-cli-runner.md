# Issue #1 — Bootstrap CLI + runner skeleton

## Title
Bootstrap ARK CLI and runner skeleton (`ark run --suite core25 --model <id>`)

## Why
Establish a stable execution interface that outputs canonical artifacts for every suite run.

## Scope
- CLI command: `ark run --suite core25 --model <id> --out <dir>`
- Artifact outputs:
  - `traces.jsonl`
  - `summary.json`
- Deterministic task execution mode for reproducibility.

## Acceptance criteria
- [ ] Running the command on a clean machine completes without manual patching.
- [ ] `summary.json` includes `task_count`, `passed`, `failed`, `reliability_at_k`.
- [ ] `traces.jsonl` includes one row per task step.
- [ ] README quickstart includes one copy-paste command.
- [ ] Test covers artifact generation.

## Labels
`good-first-issue`, `core`
