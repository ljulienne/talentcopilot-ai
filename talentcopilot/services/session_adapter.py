from typing import Any, Dict, List

from talentcopilot.models.recruitment import (
    AnalysisResult,
    CandidateProfile,
    JobProfile,
    RecruitmentSession,
)


def _safe_score(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def candidate_from_result(result: Dict[str, Any]) -> CandidateProfile:
    candidate_data = result.get("candidate") or result.get("candidate_data") or result

    name = (
        candidate_data.get("name")
        or candidate_data.get("full_name")
        or result.get("name")
        or "Unknown candidate"
    )

    score = _safe_score(
        result.get("score")
        or result.get("match_score")
        or candidate_data.get("score")
        or candidate_data.get("match_score")
    )

    confidence = _safe_score(
        result.get("decision_confidence")
        or result.get("confidence")
        or score
    )

    skills = (
        candidate_data.get("skills")
        or result.get("skills")
        or []
    )

    if isinstance(skills, str):
        skills = [skills]

    risks = result.get("risks") or candidate_data.get("risks") or []
    evidence = result.get("evidence") or candidate_data.get("evidence") or []

    return CandidateProfile(
        name=name,
        role=candidate_data.get("role") or candidate_data.get("title") or "",
        summary=result.get("summary") or candidate_data.get("summary") or "",
        skills=skills,
        score=score,
        decision_confidence=confidence,
        recommendation=result.get("recommendation") or "Review required",
        risks=risks if isinstance(risks, list) else [str(risks)],
        evidence=evidence if isinstance(evidence, list) else [str(evidence)],
        raw=result,
    )


def session_from_state(
    recruitment_context: Dict[str, Any] | None,
    analysis_batch: Dict[str, Any] | None,
) -> RecruitmentSession:
    context = recruitment_context or {}

    job = JobProfile(
        title=context.get("job_title") or context.get("title") or "Untitled recruitment",
        company=context.get("company", ""),
        department=context.get("department", ""),
        location=context.get("location", ""),
        language=context.get("language", "English"),
    )

    batch_results: List[Dict[str, Any]] = []

    if analysis_batch and analysis_batch.get("success"):
        batch_results = analysis_batch.get("results") or []

    results = [
        AnalysisResult(candidate=candidate_from_result(item), rank=index + 1)
        for index, item in enumerate(batch_results)
        if isinstance(item, dict)
    ]

    return RecruitmentSession(job=job, results=results)
