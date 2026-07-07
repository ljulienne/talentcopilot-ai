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


def _extract_score_from_match_result(match_result: Any) -> float:
    if hasattr(match_result, "overall_score"):
        return _safe_score(match_result.overall_score)

    if isinstance(match_result, dict):
        return _safe_score(
            match_result.get("overall_score")
            or match_result.get("score")
            or match_result.get("match_score")
            or match_result.get("final_score")
        )

    return 0.0


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value

    if hasattr(value, "__dict__"):
        return dict(value.__dict__)

    return {}


def candidate_from_result(result: Dict[str, Any]) -> CandidateProfile:
    result = _as_dict(result)

    candidate_data = (
        result.get("candidate")
        or result.get("candidate_data")
        or result.get("profile")
        or {}
    )

    candidate_data = _as_dict(candidate_data)

    name = (
        candidate_data.get("name")
        or candidate_data.get("full_name")
        or result.get("name")
        or result.get("candidate_name")
        or "Unknown candidate"
    )

    match_result_score = _extract_score_from_match_result(result.get("match_result"))

    score = _safe_score(
        result.get("score")
        or result.get("match_score")
        or result.get("overall_score")
        or candidate_data.get("score")
        or candidate_data.get("match_score")
        or match_result_score
    )

    confidence = _safe_score(
        result.get("decision_confidence")
        or result.get("confidence")
        or result.get("decision_score")
        or score
    )

    skills = candidate_data.get("skills") or result.get("skills") or []

    if isinstance(skills, str):
        skills = [skills]

    risks = result.get("risks") or candidate_data.get("risks") or []
    evidence = result.get("evidence") or candidate_data.get("evidence") or []

    if not isinstance(risks, list):
        risks = [str(risks)]

    if not isinstance(evidence, list):
        evidence = [str(evidence)]

    return CandidateProfile(
        name=str(name),
        role=candidate_data.get("role") or candidate_data.get("title") or result.get("role") or "",
        summary=result.get("summary") or candidate_data.get("summary") or "",
        skills=skills,
        score=score,
        decision_confidence=confidence,
        recommendation=result.get("recommendation") or "Review required",
        risks=risks,
        evidence=evidence,
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
    ]

    return RecruitmentSession(job=job, results=results)
