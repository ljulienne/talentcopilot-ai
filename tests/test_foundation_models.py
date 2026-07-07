from talentcopilot.models.recruitment import AnalysisResult, CandidateProfile, JobProfile, RecruitmentSession
from talentcopilot.services.session_adapter import session_from_state


def test_recruitment_session_ranking():
    session = RecruitmentSession(
        job=JobProfile(title="Data Analyst"),
        results=[
            AnalysisResult(candidate=CandidateProfile(name="Bob", decision_confidence=74)),
            AnalysisResult(candidate=CandidateProfile(name="Alice", decision_confidence=91)),
        ],
    )

    assert session.total_candidates == 2
    assert session.best_candidate.name == "Alice"
    assert session.average_confidence == 82.5


def test_session_adapter_from_analysis_batch():
    context = {
        "job_title": "Transformation Lead",
        "company": "ACME",
    }

    batch = {
        "success": True,
        "results": [
            {
                "candidate": {"name": "Alice Martin", "skills": ["Project Management"]},
                "score": 88,
                "recommendation": "Strong candidate",
            }
        ],
    }

    session = session_from_state(context, batch)

    assert session.job.title == "Transformation Lead"
    assert session.job.company == "ACME"
    assert session.total_candidates == 1
    assert session.best_candidate.name == "Alice Martin"
    assert session.best_candidate.decision_confidence == 88
