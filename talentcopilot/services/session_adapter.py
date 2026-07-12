from typing import Any, Dict, List

from talentcopilot.models.recruitment import AnalysisResult, CandidateProfile, JobProfile, RecruitmentSession


def _safe_score(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _first_present(*values: Any) -> Any:
    """Return the first supplied value that is not None.

    Unlike ``or`` chains, this preserves valid numeric zero scores.
    """
    for value in values:
        if value is not None:
            return value
    return None


def _extract_score_from_match_result(match_result: Any) -> float:
    if hasattr(match_result, "overall_score"):
        return _safe_score(match_result.overall_score)
    if isinstance(match_result, dict):
        return _safe_score(_first_present(
            match_result.get("overall_score"),
            match_result.get("score"),
            match_result.get("match_score"),
            match_result.get("final_score"),
        ))
    return 0.0


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def candidate_from_result(result: Dict[str, Any]) -> CandidateProfile:
    result = _as_dict(result)
    candidate_data = _as_dict(_first_present(
        result.get("candidate"), result.get("candidate_data"), result.get("profile"), {}
    ))

    name = _first_present(
        candidate_data.get("name"), candidate_data.get("full_name"),
        result.get("name"), result.get("candidate_name"), "Unknown candidate"
    )
    match_result_score = _extract_score_from_match_result(result.get("match_result"))
    score = _safe_score(_first_present(
        result.get("score"), result.get("match_score"), result.get("overall_score"),
        candidate_data.get("score"), candidate_data.get("match_score"), match_result_score,
    ))
    confidence = _safe_score(_first_present(
        result.get("decision_confidence"), result.get("confidence"),
        result.get("decision_score"), score,
    ))

    skills = _first_present(candidate_data.get("skills"), result.get("skills"), [])
    if isinstance(skills, str):
        skills = [skills]
    risks = _first_present(result.get("risks"), candidate_data.get("risks"), [])
    evidence = _first_present(result.get("evidence"), candidate_data.get("evidence"), [])
    if not isinstance(risks, list):
        risks = [str(risks)]
    if not isinstance(evidence, list):
        evidence = [str(evidence)]

    return CandidateProfile(
        name=str(name),
        role=_first_present(candidate_data.get("role"), candidate_data.get("title"), result.get("role"), ""),
        summary=_first_present(result.get("summary"), candidate_data.get("summary"), ""),
        skills=skills,
        score=score,
        decision_confidence=confidence,
        recommendation=_first_present(result.get("recommendation"), "Review required"),
        risks=risks,
        evidence=evidence,
        raw=result,
    )


def session_from_state(recruitment_context: Dict[str, Any] | None, analysis_batch: Dict[str, Any] | None) -> RecruitmentSession:
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

    candidates = [candidate_from_result(item) for item in batch_results]
    candidates.sort(key=lambda item: (-float(item.score), item.name))
    results = [AnalysisResult(candidate=candidate, rank=index + 1) for index, candidate in enumerate(candidates)]
    return RecruitmentSession(job=job, results=results)
