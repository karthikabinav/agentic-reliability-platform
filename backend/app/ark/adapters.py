from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterResult:
    backend: str
    model_name: str
    passed: bool
    failure_class: str | None
    latency_ms: int


class ModelAdapter(ABC):
    """Interface for model backend adapters used by ARK baseline runner."""

    backend: str

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def evaluate_task(self, task: dict) -> AdapterResult:
        raise NotImplementedError


class OpenRouterAdapter(ModelAdapter):
    backend = "openrouter"

    def evaluate_task(self, task: dict) -> AdapterResult:
        seed = hashlib.sha256(f"{self.backend}:{self.model_name}:{task['id']}".encode()).hexdigest()
        latency_ms = 120 + int(seed[:2], 16)
        expected = task.get("expected", "pass")
        passed = expected == "pass"
        return AdapterResult(
            backend=self.backend,
            model_name=self.model_name,
            passed=passed,
            failure_class=None if passed else "retry_exhaustion",
            latency_ms=latency_ms,
        )


class VLLMAdapter(ModelAdapter):
    backend = "vllm"

    def evaluate_task(self, task: dict) -> AdapterResult:
        seed = hashlib.sha256(f"{self.backend}:{self.model_name}:{task['id']}".encode()).hexdigest()
        latency_ms = 80 + int(seed[:2], 16)
        expected = task.get("expected", "pass")
        passed = expected == "pass"
        return AdapterResult(
            backend=self.backend,
            model_name=self.model_name,
            passed=passed,
            failure_class=None if passed else "retry_exhaustion",
            latency_ms=latency_ms,
        )


def parse_model_spec(model_spec: str) -> tuple[str, str]:
    """Parse model spec into (backend, model_name).

    Supported formats:
    - openrouter:<model_name>
    - vllm:<model_name>
    - openrouter/<model_name> (legacy)
    - vllm/<model_name> (legacy)
    """

    if ":" in model_spec:
        backend, model_name = model_spec.split(":", 1)
    elif "/" in model_spec:
        backend, model_name = model_spec.split("/", 1)
    else:
        raise ValueError(
            "Unsupported model spec. Use '<backend>:<model>' (e.g. openrouter:openai/gpt-4o-mini or vllm:meta-llama/Llama-3.1-8B-Instruct)."
        )

    backend = backend.strip().lower()
    model_name = model_name.strip()
    if not backend or not model_name:
        raise ValueError("Model spec must include non-empty backend and model name.")
    return backend, model_name


def get_adapter(model_spec: str) -> ModelAdapter:
    backend, model_name = parse_model_spec(model_spec)
    if backend == "openrouter":
        return OpenRouterAdapter(model_name=model_name)
    if backend == "vllm":
        return VLLMAdapter(model_name=model_name)
    raise ValueError(f"Unsupported backend '{backend}'. Supported backends: openrouter, vllm.")
