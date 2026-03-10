import json
import subprocess
import sys
from pathlib import Path

from app.ark.adapters import OpenRouterAdapter, VLLMAdapter, get_adapter
from app.ark.cli import run


def test_adapter_selection_smoke():
    assert isinstance(get_adapter("openrouter:openai/gpt-4o-mini"), OpenRouterAdapter)
    assert isinstance(get_adapter("vllm:meta-llama/Llama-3.1-8B-Instruct"), VLLMAdapter)
    # legacy slash format remains supported
    assert isinstance(get_adapter("openrouter/auto"), OpenRouterAdapter)


def test_run_includes_adapter_metadata(tmp_path: Path):
    out = tmp_path / "artifacts"
    summary = run(suite="core25", model="vllm:meta-llama/Llama-3.1-8B-Instruct", out=out)

    assert summary["backend"] == "vllm"
    assert summary["model_name"] == "meta-llama/Llama-3.1-8B-Instruct"

    first_trace = json.loads((out / "traces.jsonl").read_text().splitlines()[0])
    assert first_trace["backend"] == "vllm"
    assert first_trace["model_name"] == "meta-llama/Llama-3.1-8B-Instruct"


def test_cli_baseline_run_command_smoke(tmp_path: Path):
    out = tmp_path / "baseline"
    backend_dir = Path(__file__).resolve().parents[1]

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.ark.cli",
            "run",
            "--suite",
            "core25",
            "--model",
            "openrouter:openai/gpt-4o-mini",
            "--out",
            str(out),
        ],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    summary = json.loads(proc.stdout)
    assert summary["backend"] == "openrouter"
    assert (out / "summary.json").exists()
    assert (out / "traces.jsonl").exists()
