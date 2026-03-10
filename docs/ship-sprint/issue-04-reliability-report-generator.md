# Issue #4 — Reliability report generator

## Title
Generate Markdown + CSV reliability reports from run artifacts

## Why
Need a shareable output for maintainers/contributors to inspect failures and prioritize fixes.

## Scope
- Input: `traces.jsonl` + `summary.json`
- Output:
  - `reliability-report.md`
  - `reliability-report.csv`
- Include per-task failure taxonomy and top-3 fix suggestions.

## Acceptance criteria
- [ ] Single command generates both report formats.
- [ ] Markdown report includes totals + Reliability@K + failure table.
- [ ] CSV is analysis-friendly (one row per task/event aggregate).
- [ ] Top-3 fix suggestion section present.

## Labels
`reporting`, `good-first-issue`
