import json
from datetime import datetime
from pathlib import Path

from app.ark.cli import run


def _validate_type(value, expected_type):
    if isinstance(expected_type, list):
        return any(_validate_type(value, t) for t in expected_type)

    mapping = {
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "null": lambda v: v is None,
        "object": lambda v: isinstance(v, dict),
    }
    if expected_type not in mapping:
        raise AssertionError(f"unsupported schema type in lightweight validator: {expected_type}")
    return mapping[expected_type](value)


def _validate_with_lightweight_schema(row: dict, schema: dict) -> None:
    assert isinstance(row, dict)

    required = schema.get("required", [])
    for field in required:
        assert field in row, f"missing required field: {field}"

    if schema.get("additionalProperties") is False:
        allowed = set(schema.get("properties", {}).keys())
        assert set(row.keys()).issubset(allowed), "unexpected fields present"

    for name, rules in schema.get("properties", {}).items():
        if name not in row:
            continue
        value = row[name]

        if "type" in rules:
            assert _validate_type(value, rules["type"]), f"field {name} has invalid type"

        if "minLength" in rules and isinstance(value, str):
            assert len(value) >= rules["minLength"], f"field {name} shorter than minLength"

        if "minimum" in rules and isinstance(value, int):
            assert value >= rules["minimum"], f"field {name} less than minimum"

        if "enum" in rules:
            assert value in rules["enum"], f"field {name} not in enum"

        if rules.get("format") == "date-time" and value is not None:
            datetime.fromisoformat(value.replace("Z", "+00:00"))


def _validate_row_against_schema(row: dict, schema: dict) -> None:
    try:
        import jsonschema  # type: ignore

        jsonschema.validate(instance=row, schema=schema)
    except ModuleNotFoundError:
        _validate_with_lightweight_schema(row=row, schema=schema)


def test_ark_traces_validate_against_v0_schema(tmp_path: Path):
    out = tmp_path / "artifacts"
    run(suite="core25", model="openrouter/auto", out=out)

    schema_path = Path(__file__).resolve().parents[1] / "app" / "ark" / "schemas" / "trace.schema.v0.json"
    schema = json.loads(schema_path.read_text())

    trace_rows = [
        json.loads(line)
        for line in (out / "traces.jsonl").read_text().splitlines()
        if line.strip()
    ]

    assert trace_rows, "traces.jsonl should contain at least one row"
    for row in trace_rows:
        _validate_row_against_schema(row=row, schema=schema)
