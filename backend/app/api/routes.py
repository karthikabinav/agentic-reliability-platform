from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.db.models import ObsEvent, ReplayJob
from app.db.session import get_db
from app.services.schemas import IngestRequest, IngestResponse, ReplayRequest

router = APIRouter(prefix="/v1/observability", tags=["observability"])


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.post("/events", response_model=IngestResponse)
def ingest_events(payload: IngestRequest, db: Session = Depends(get_db)) -> IngestResponse:
    errors: list[str] = []
    accepted = 0
    for i, e in enumerate(payload.events):
        try:
            # Enforce MVP observability contract for prompts/tool-calls/model tracking
            if e.event_type == "prompt_logged":
                if not isinstance(e.payload, dict) or not e.payload.get("prompt"):
                    raise ValueError("prompt_logged requires payload.prompt")
                if not e.model_version:
                    raise ValueError("prompt_logged requires model_version")

            if e.event_type in {"tool_call_started", "tool_call_finished"}:
                if not isinstance(e.payload, dict) or not e.payload.get("tool_name"):
                    raise ValueError(f"{e.event_type} requires payload.tool_name")
                if not e.model_version:
                    raise ValueError(f"{e.event_type} requires model_version")

            db.add(
                ObsEvent(
                    tenant_id=payload.tenant_id,
                    trace_id=e.trace_id,
                    span_id=e.span_id,
                    parent_span_id=e.parent_span_id,
                    workflow_id=e.workflow_id,
                    agent_id=e.agent_id,
                    task_id=e.task_id,
                    event_type=e.event_type,
                    skill_tag=e.skill_tag,
                    failure_class=e.failure_class,
                    payload=e.payload,
                    policy_version=e.policy_version,
                    model_version=e.model_version,
                    ts=e.ts or datetime.utcnow(),
                )
            )
            accepted += 1
        except Exception as ex:
            errors.append(f"event[{i}] rejected: {ex}")
    db.commit()
    return IngestResponse(accepted=accepted, rejected=len(errors), errors=errors)


@router.get("/traces/{trace_id}")
def trace(trace_id: str, db: Session = Depends(get_db)):
    rows = db.scalars(select(ObsEvent).where(ObsEvent.trace_id == trace_id).order_by(ObsEvent.ts.asc())).all()
    return {
        "trace_id": trace_id,
        "events": [
            {
                "id": r.id,
                "tenant_id": r.tenant_id,
                "span_id": r.span_id,
                "parent_span_id": r.parent_span_id,
                "workflow_id": r.workflow_id,
                "agent_id": r.agent_id,
                "task_id": r.task_id,
                "event_type": r.event_type,
                "skill_tag": r.skill_tag,
                "failure_class": r.failure_class,
                "payload": r.payload,
                "policy_version": r.policy_version,
                "model_version": r.model_version,
                "ts": r.ts.isoformat(),
            }
            for r in rows
        ],
    }


@router.get("/search")
def search(
    tenant_id: str,
    workflow_id: str | None = None,
    event_type: str | None = None,
    skill_tag: str | None = None,
    failure_class: str | None = None,
    model_version: str | None = None,
    tool_name: str | None = None,
    has_prompt: bool | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    stmt = select(ObsEvent).where(ObsEvent.tenant_id == tenant_id)
    if workflow_id:
        stmt = stmt.where(ObsEvent.workflow_id == workflow_id)
    if event_type:
        stmt = stmt.where(ObsEvent.event_type == event_type)
    if skill_tag:
        stmt = stmt.where(ObsEvent.skill_tag == skill_tag)
    if failure_class:
        stmt = stmt.where(ObsEvent.failure_class == failure_class)
    if model_version:
        stmt = stmt.where(ObsEvent.model_version == model_version)
    rows = db.scalars(stmt.order_by(ObsEvent.ts.desc()).limit(max(limit * 5, 200))).all()

    filtered = []
    for r in rows:
        p = r.payload or {}
        if tool_name and p.get("tool_name") != tool_name:
            continue
        if has_prompt is True and not p.get("prompt"):
            continue
        if has_prompt is False and p.get("prompt"):
            continue
        filtered.append(r)
        if len(filtered) >= limit:
            break

    return {
        "count": len(filtered),
        "items": [
            {
                "id": r.id,
                "trace_id": r.trace_id,
                "event_type": r.event_type,
                "skill_tag": r.skill_tag,
                "failure_class": r.failure_class,
                "model_version": r.model_version,
                "tool_name": (r.payload or {}).get("tool_name"),
                "has_prompt": bool((r.payload or {}).get("prompt")),
                "ts": r.ts.isoformat(),
            }
            for r in filtered
        ],
    }


@router.get("/metrics")
def metrics(tenant_id: str, workflow_id: str | None = None, db: Session = Depends(get_db)):
    base = select(ObsEvent).where(ObsEvent.tenant_id == tenant_id)
    if workflow_id:
        base = base.where(ObsEvent.workflow_id == workflow_id)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    failures = db.scalar(select(func.count()).select_from(base.where(ObsEvent.failure_class.is_not(None)).subquery())) or 0
    escalations = db.scalar(select(func.count()).select_from(base.where(ObsEvent.event_type == "human_escalation_triggered").subquery())) or 0
    tool_calls = db.scalar(select(func.count()).select_from(base.where(ObsEvent.event_type == "tool_call_started").subquery())) or 0
    prompt_events = db.scalar(select(func.count()).select_from(base.where(ObsEvent.event_type == "prompt_logged").subquery())) or 0
    modeled_events = db.scalar(select(func.count()).select_from(base.where(ObsEvent.model_version.is_not(None)).subquery())) or 0

    return {
        "tenant_id": tenant_id,
        "workflow_id": workflow_id,
        "totals": {
            "events": int(total),
            "failures": int(failures),
            "escalations": int(escalations),
            "tool_calls": int(tool_calls),
            "prompt_events": int(prompt_events),
            "modeled_events": int(modeled_events),
        },
        "rates": {
            "failure_rate": float(failures / total) if total else 0.0,
            "escalation_rate": float(escalations / total) if total else 0.0,
            "prompt_coverage_rate": float(prompt_events / total) if total else 0.0,
            "model_coverage_rate": float(modeled_events / total) if total else 0.0,
        },
    }


@router.get("/metrics/skills")
def skill_metrics(tenant_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            ObsEvent.skill_tag,
            func.count().label("total"),
            func.sum(case((ObsEvent.failure_class.is_not(None), 1), else_=0)).label("failures"),
        )
        .where(ObsEvent.tenant_id == tenant_id)
        .group_by(ObsEvent.skill_tag)
    ).all()

    items = []
    for skill, total, failures in rows:
        total = int(total or 0)
        failures = int(failures or 0)
        items.append(
            {
                "skill_tag": skill or "unlabeled",
                "events": total,
                "failures": failures,
                "failure_rate": (failures / total) if total else 0.0,
            }
        )
    items.sort(key=lambda x: x["events"], reverse=True)
    return {"tenant_id": tenant_id, "skills": items}


@router.post("/replay")
def submit_replay(payload: ReplayRequest, db: Session = Depends(get_db)):
    replay_id = f"rp_{uuid4().hex[:10]}"
    db.add(
        ReplayJob(
            replay_id=replay_id,
            trace_id=payload.trace_id,
            mode=payload.mode,
            target_policy_version=payload.target_policy_version,
            target_model_version=payload.target_model_version,
            status="queued",
            result={"note": "MVP stub: execute replay worker in P1"},
        )
    )
    db.commit()
    return {"replay_id": replay_id, "status": "queued"}


@router.get("/replay/{replay_id}")
def replay_status(replay_id: str, db: Session = Depends(get_db)):
    row = db.scalar(select(ReplayJob).where(ReplayJob.replay_id == replay_id))
    if not row:
        return {"error": "not_found"}
    return {"replay_id": row.replay_id, "status": row.status, "result": row.result}
