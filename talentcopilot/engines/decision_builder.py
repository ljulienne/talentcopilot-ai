from typing import Any, Dict, List

from talentcopilot.domain import (
    Application,
    CandidateDecision,
    CandidateProfile,
    Evidence,
    InterviewPlan,
)


def build_candidate_profile(item: Dict[str, Any]) -> CandidateProfile:
    candidate = item.get("candidate")

    capabilities = getattr(candidate, "capabilities", []) or []

    return CandidateProfile(
        candidate_id=getattr(candidate, "name", "unknown").lower().replace(" ", "-"),
        name=getattr(candidate, "name", "Unknown Candidate"),
        current_role=getattr(candidate, "current_role", ""),
        skills=[getattr(cap, "name", "") for cap in capabilities],
    )


def build_evidence_objects(item: Dict[str, Any]) -> List[Evidence]:
    evidence_items = item.get("evidence", []) or []

    return [
        Evidence(
            competency=e.get("competency", ""),
            status=e.get("status", ""),
            score=e.get("score", 0),
            confidence=e.get("confidence", 0),
            excerpts=e.get("excerpts", []),
            recommendation=e.get("recommendation", ""),
        )
        for e in evidence_items
    ]


def build_interview_plan(item: Dict[str, Any]) -> InterviewPlan:
    match = item.get("match_result")
    questions = getattr(match, "interview_questions", []) or []

    return InterviewPlan(
        focus_areas=[getattr(q, "linked_competency", "") for q in questions],
        questions=[getattr(q, "question", "") for q in questions],
    )


def build_candidate_decision(item: Dict[str, Any]) -> CandidateDecision:
    candidate_profile = build_candidate_profile(item)
    match = item.get("match_result")
    intelligence = item.get("candidate_intelligence", {}) or {}

    application = Application(
        application_id=f"app-{candidate_profile.candidate_id}",
        candidate=candidate_profile,
        job_title=getattr(getattr(match, "job", None), "title", ""),
        source_file=item.get("file", ""),
    )

    return CandidateDecision(
        application=application,
        match_score=getattr(match, "overall_score", 0),
        rank=item.get("rank"),
        recommendation=getattr(match, "recommendation", ""),
        confidence=getattr(match, "confidence_score", 0),
        evidence=build_evidence_objects(item),
        risks=intelligence.get("risk_factors", []),
        strengths=intelligence.get("strengths", []),
        interview_plan=build_interview_plan(item),
        executive_summary=getattr(match, "executive_summary", ""),
        next_action="Proceed according to the hiring recommendation.",
    )


def enrich_with_candidate_decisions(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []

    for item in results:
        item["candidate_decision"] = build_candidate_decision(item)
        enriched.append(item)

    return enriched
