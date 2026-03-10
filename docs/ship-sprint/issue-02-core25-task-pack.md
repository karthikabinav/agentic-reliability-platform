# Issue #2 — Core25 task pack (tool-use + recovery)

## Title
Implement Core25 YAML/JSON task pack with pass/fail contracts

## Why
Need a compact but representative benchmark set for tool-use reliability and recovery behavior.

## Scope
- Expand suite from scaffold subset to full 25 tasks.
- Include at least 5 adversarial/recovery tasks.
- Each task must define:
  - id
  - category
  - prompt
  - expected outcome contract

## Acceptance criteria
- [ ] 25 tasks are loadable and runnable end-to-end.
- [ ] Categories include tool-use, planning, recovery, adversarial.
- [ ] At least 5 tasks specifically test recovery/adversarial patterns.
- [ ] Task spec format documented.

## Labels
`benchmark`, `high-impact`
