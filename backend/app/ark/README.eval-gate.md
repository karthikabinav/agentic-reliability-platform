# Eval Gate (Reliability Release Check)

Use this after `ark run` to fail CI/CD when reliability drops below policy.

## Command
```bash
ark gate --in ./artifacts/core25 --min-reliability 0.80 --max-failed-tasks 5
```

## Behavior
- Reads `summary.json` from `--in`
- Prints a JSON gate verdict
- Exit code `0` if gate passes, `1` if gate fails

## Typical flow
```bash
ark run --suite core25 --model openrouter:openai/gpt-4o-mini --out ./artifacts/core25
ark report --in ./artifacts/core25 --out ./artifacts/core25
ark gate --in ./artifacts/core25 --min-reliability 0.80 --max-failed-tasks 5
```
