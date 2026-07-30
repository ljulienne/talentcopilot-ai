"""Versioned persistence for canonical recruitment decision projects.

Release 8.4.0 stores a RecruitmentSession together with its workflow context in
JSON. Persistence is explicit for a new upload and becomes automatic only after
that project has been saved once. This avoids silently writing candidate data
while still allowing a recruiter to resume a saved decision workspace.
"""

from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from types import SimpleNamespace
from typing import Any, Mapping, Optional

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.services.candidate_identity import resolve_candidate_id
from talentcopilot.storage.recruitment_store import load_recruitment, save_recruitment


PROJECT_SCHEMA_VERSION = "talentcopilot-recruitment-project-v1"
PERSISTENCE_FLAG = "project_persistence_enabled"
PROJECT_SCHEMA_KEY = "project_schema_version"


def _enum_value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if hasattr(value, "model_dump"):
        try:
            return _json_safe(value.model_dump())
        except Exception:
            pass
    if hasattr(value, "dict"):
        try:
            return _json_safe(value.dict())
        except Exception:
            pass
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "__dict__"):
        return _json_safe(vars(value))
    return str(value)


def _attribute_tree(value: Any) -> Any:
    """Restore report-like dictionaries with attribute access.

    Official scores, ranks and score breakdowns are restored directly on the
    canonical analysis model. Optional presentation reports are restored as
    lightweight namespaces so existing ``getattr`` consumers keep working.
    """

    if isinstance(value, Mapping):
        return SimpleNamespace(
            **{str(key): _attribute_tree(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return [_attribute_tree(item) for item in value]
    return value


def _status(value: Any, enum_type, fallback):
    raw = _enum_value(value)
    for member in enum_type:
        if raw in {member.value, member.name}:
            return member
    return fallback


def _workflow_payload(context: RecruitmentWorkflowContext | None) -> dict[str, Any]:
    if context is None:
        return {}
    return _json_safe(asdict(context))


def workflow_context_from_payload(payload: Mapping[str, Any] | None) -> RecruitmentWorkflowContext:
    raw = dict(payload or {})
    allowed = {item.name for item in fields(RecruitmentWorkflowContext)}
    values = {key: raw[key] for key in allowed if key in raw}
    return RecruitmentWorkflowContext(**values)


def _analysis_payload(analysis: Any) -> dict[str, Any]:
    return {
        "candidate_name": str(getattr(analysis, "candidate_name", "Candidate") or "Candidate"),
        "candidate_id": str(getattr(analysis, "candidate_id", "") or ""),
        "status": _enum_value(getattr(analysis, "status", CandidateAnalysisStatus.PENDING)),
        "match_score": float(getattr(analysis, "match_score", 0.0) or 0.0),
        "decision_score": getattr(analysis, "decision_score", None),
        "rank": getattr(analysis, "rank", None),
        "score_breakdown": _json_safe(dict(getattr(analysis, "score_breakdown", {}) or {})),
        "governance_report": _json_safe(getattr(analysis, "governance_report", None)),
        "decision_report": _json_safe(getattr(analysis, "decision_report", None)),
        "recruiter_copilot_report": _json_safe(getattr(analysis, "recruiter_copilot_report", None)),
        "talent_locator_result": _json_safe(getattr(analysis, "talent_locator_result", None)),
        "errors": _json_safe(list(getattr(analysis, "errors", []) or [])),
        "notes": _json_safe(list(getattr(analysis, "notes", []) or [])),
    }


def _analysis_from_payload(payload: Mapping[str, Any]) -> CandidateAnalysisState:
    score = payload.get("decision_score")
    try:
        decision_score = None if score is None else float(score)
    except (TypeError, ValueError):
        decision_score = None
    rank = payload.get("rank")
    try:
        rank_value = None if rank is None else int(rank)
    except (TypeError, ValueError):
        rank_value = None
    return CandidateAnalysisState(
        candidate_name=str(payload.get("candidate_name") or "Candidate"),
        candidate_id=str(payload.get("candidate_id") or ""),
        status=_status(
            payload.get("status"),
            CandidateAnalysisStatus,
            CandidateAnalysisStatus.PENDING,
        ),
        match_score=float(payload.get("match_score") or 0.0),
        decision_score=decision_score,
        rank=rank_value,
        score_breakdown=dict(payload.get("score_breakdown") or {}),
        governance_report=_attribute_tree(payload.get("governance_report")) if payload.get("governance_report") is not None else None,
        decision_report=_attribute_tree(payload.get("decision_report")) if payload.get("decision_report") is not None else None,
        recruiter_copilot_report=_attribute_tree(payload.get("recruiter_copilot_report")) if payload.get("recruiter_copilot_report") is not None else None,
        talent_locator_result=_attribute_tree(payload.get("talent_locator_result")) if payload.get("talent_locator_result") is not None else None,
        errors=[str(item) for item in list(payload.get("errors") or [])],
        notes=[str(item) for item in list(payload.get("notes") or [])],
    )


def _compatibility_analysis_batch(session: RecruitmentSession) -> dict[str, Any]:
    candidates_by_id = {
        str(candidate.get("candidate_id") or ""): candidate
        for candidate in list(session.candidates or [])
        if isinstance(candidate, Mapping)
    }
    candidates_by_name = {
        str(candidate.get("name") or ""): candidate
        for candidate in list(session.candidates or [])
        if isinstance(candidate, Mapping)
    }
    results = []
    for analysis in session.ranked_analyses:
        candidate = candidates_by_id.get(str(analysis.candidate_id or "")) or candidates_by_name.get(analysis.candidate_name) or {"name": analysis.candidate_name}
        results.append(
            {
                "candidate": _json_safe(candidate),
                "candidate_id": str(analysis.candidate_id or ""),
                "candidate_name": analysis.candidate_name,
                "match_score": float(analysis.match_score or 0.0),
                "decision_score": analysis.decision_score,
                "rank": analysis.rank,
                "score_breakdown": _json_safe(analysis.score_breakdown),
            }
        )
    return {"success": True, "results": results}


def project_payload(
    session: RecruitmentSession,
    workflow_context: RecruitmentWorkflowContext | None = None,
    *,
    analysis_batch: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = dict(getattr(session, "metadata", {}) or {})
    metadata[PERSISTENCE_FLAG] = True
    metadata[PROJECT_SCHEMA_KEY] = PROJECT_SCHEMA_VERSION
    workflow_payload = _workflow_payload(workflow_context)
    management = dict(metadata.get("project_management") or {})
    if workflow_payload:
        management.setdefault("version", "talentcopilot-project-portfolio-v1")
        management["workflow_context"] = {
            "decision_recorded": bool(workflow_payload.get("decision_recorded")),
            "finalists_compared": bool(workflow_payload.get("finalists_compared")),
            "interview_assessed_candidate_ids": list(workflow_payload.get("interview_assessed_candidate_ids") or []),
            "interview_prepared_candidate_ids": list(workflow_payload.get("interview_prepared_candidate_ids") or []),
        }
        management["interview_count"] = len(workflow_payload.get("interview_assessed_candidate_ids") or [])
        management["finalist_count"] = len(workflow_payload.get("finalist_candidate_ids") or [])
        metadata["project_management"] = management
    session.metadata = metadata
    batch = dict(analysis_batch or {}) if isinstance(analysis_batch, Mapping) else _compatibility_analysis_batch(session)
    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "id": str(session.session_id),
        "title": str(session.role_title),
        "status": _enum_value(session.status),
        "created_at": str(session.created_at),
        "updated_at": str(session.updated_at),
        "candidate_count": int(session.candidate_count),
        "analyzed_count": int(session.analyzed_count),
        "job": _json_safe(session.job),
        "candidates": _json_safe(session.candidates),
        "analyses": [_analysis_payload(item) for item in list(session.analyses or [])],
        "metadata": _json_safe(metadata),
        "workflow_context": workflow_payload,
        "analysis_batch": _json_safe(batch),
    }


def save_project(
    session: RecruitmentSession,
    workflow_context: RecruitmentWorkflowContext | None = None,
    *,
    analysis_batch: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if session is None:
        raise ValueError("A recruitment session is required.")
    payload = project_payload(session, workflow_context, analysis_batch=analysis_batch)
    saved = save_recruitment(payload)
    session.metadata[PERSISTENCE_FLAG] = True
    session.metadata[PROJECT_SCHEMA_KEY] = PROJECT_SCHEMA_VERSION
    return saved


def session_from_project_payload(data: Mapping[str, Any]) -> RecruitmentSession:
    """Restore the canonical session, with backward compatibility for legacy files."""

    if data.get("schema_version") != PROJECT_SCHEMA_VERSION:
        return _legacy_session(data)

    analyses = [
        _analysis_from_payload(item)
        for item in list(data.get("analyses") or [])
        if isinstance(item, Mapping)
    ]
    metadata = dict(data.get("metadata") or {})
    metadata[PERSISTENCE_FLAG] = True
    metadata[PROJECT_SCHEMA_KEY] = PROJECT_SCHEMA_VERSION
    session = RecruitmentSession(
        session_id=str(data.get("id") or "saved-recruitment"),
        job=dict(data.get("job") or {}),
        candidates=[dict(item) for item in list(data.get("candidates") or []) if isinstance(item, Mapping)],
        status=_status(data.get("status"), SessionStatus, SessionStatus.READY),
        analyses=analyses,
        created_at=str(data.get("created_at") or ""),
        updated_at=str(data.get("updated_at") or ""),
        metadata=metadata,
    )
    # A persisted source-of-truth snapshot must still match the restored scores
    # and candidate identities. This guards against silent rank drift.
    RecruitmentSourceOfTruthService().get(session, validate=True)
    return session


def _legacy_session(data: Mapping[str, Any]) -> RecruitmentSession:
    context = data.get("recruitment_context") if isinstance(data.get("recruitment_context"), Mapping) else {}
    title = str(data.get("title") or context.get("title") or context.get("job_title") or "Untitled recruitment")
    job = dict(data.get("job") or {}) if isinstance(data.get("job"), Mapping) else {}
    job.setdefault("title", title)
    batch = data.get("analysis_batch") if isinstance(data.get("analysis_batch"), Mapping) else {}
    raw_results = batch.get("results") if isinstance(batch.get("results"), list) else []
    candidates: list[dict[str, Any]] = []
    analyses: list[CandidateAnalysisState] = []
    for index, raw in enumerate(raw_results, start=1):
        result = raw if isinstance(raw, Mapping) else {}
        candidate = result.get("candidate") or result.get("candidate_data") or result.get("profile") or {}
        candidate_dict = dict(candidate) if isinstance(candidate, Mapping) else {}
        name = str(candidate_dict.get("name") or result.get("candidate_name") or f"Candidate {index}")
        candidate_dict.setdefault("name", name)
        candidate_id = str(candidate_dict.get("candidate_id") or result.get("candidate_id") or "")
        if not candidate_id:
            candidate_id = resolve_candidate_id(candidate_dict)
        candidate_dict["candidate_id"] = candidate_id
        candidates.append(candidate_dict)
        analyses.append(
            CandidateAnalysisState(
                candidate_name=name,
                candidate_id=candidate_id,
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=float(result.get("match_score") or result.get("score") or result.get("overall_score") or 0.0),
                decision_score=result.get("decision_score"),
                rank=int(result.get("rank") or index),
                score_breakdown=dict(result.get("score_breakdown") or {}),
                notes=[str(result.get("recommendation"))] if result.get("recommendation") else [],
            )
        )
    status = SessionStatus.COMPLETED if analyses and len(analyses) == len(candidates) else SessionStatus.READY
    metadata = dict(data.get("metadata") or {})
    metadata.update({"source": "project_hub", PERSISTENCE_FLAG: True, PROJECT_SCHEMA_KEY: "legacy"})
    session = RecruitmentSession(
        session_id=str(data.get("id") or "saved-recruitment"),
        job=job,
        candidates=candidates,
        status=status,
        analyses=analyses,
        created_at=str(data.get("created_at") or ""),
        updated_at=str(data.get("updated_at") or ""),
        metadata=metadata,
    )
    if analyses:
        RecruitmentSourceOfTruthService().freeze(session, replace=True)
    return session


def load_project(project_id: str) -> tuple[RecruitmentSession, RecruitmentWorkflowContext, dict[str, Any]]:
    data = load_recruitment(project_id)
    session = session_from_project_payload(data)
    workflow = workflow_context_from_payload(data.get("workflow_context"))
    if not workflow.session_id:
        workflow.session_id = session.session_id
    if not workflow.role_title or workflow.role_title == "Recruitment":
        workflow.role_title = session.role_title
    return session, workflow, data


def persistence_enabled(session: Any) -> bool:
    metadata = getattr(session, "metadata", {}) or {}
    return bool(metadata.get(PERSISTENCE_FLAG))


def persist_project_best_effort(
    session: RecruitmentSession | None,
    workflow_context: RecruitmentWorkflowContext | None = None,
    *,
    force: bool = False,
) -> bool:
    if session is None:
        return False
    if not force and not persistence_enabled(session):
        return False
    try:
        analysis_batch: Optional[Mapping[str, Any]] = None
        if workflow_context is None:
            try:
                import streamlit as st
                from talentcopilot.services.recruitment_workflow_state import WORKFLOW_CONTEXT_KEY

                current = st.session_state.get(WORKFLOW_CONTEXT_KEY)
                if isinstance(current, RecruitmentWorkflowContext):
                    workflow_context = current
                raw_batch = st.session_state.get("analysis_batch")
                if isinstance(raw_batch, Mapping):
                    analysis_batch = raw_batch
            except Exception:
                pass
        save_project(session, workflow_context, analysis_batch=analysis_batch)
        return True
    except Exception:
        return False
