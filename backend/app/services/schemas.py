from datetime import datetime
from pydantic import BaseModel, Field


class EventIn(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    workflow_id: str
    agent_id: str
    task_id: str
    event_type: str
    skill_tag: str | None = None
    failure_class: str | None = None
    payload: dict = Field(default_factory=dict)
    policy_version: str | None = None
    model_version: str | None = None
    ts: datetime | None = None


# Optional stricter event type guidance for clients:
# - prompt_logged: payload requires {"prompt": "..."}, model_version required
# - tool_call_started/tool_call_finished: payload requires {"tool_name": "..."}, model_version required


class IngestRequest(BaseModel):
    tenant_id: str
    events: list[EventIn]


class IngestResponse(BaseModel):
    accepted: int
    rejected: int
    errors: list[str]


class ReplayRequest(BaseModel):
    trace_id: str
    mode: str
    target_policy_version: str | None = None
    target_model_version: str | None = None
