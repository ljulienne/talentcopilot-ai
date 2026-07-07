from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)


def test_recruitment_session_counts():
    session = RecruitmentSession(
        session_id="session-test",
        job={"title": "Transformation Lead"},
        candidates=[{"name": "Alice"}, {"name": "Bob"}],
        status=SessionStatus.READY,
    )

    session.add_analysis(
        CandidateAnalysisState(
            candidate_name="Alice",
            status=CandidateAnalysisStatus.ANALYZED,
            match_score=90,
            rank=1,
        )
    )

    session.add_analysis(
        CandidateAnalysisState(
            candidate_name="Bob",
            status=CandidateAnalysisStatus.ERROR,
            errors=["Missing CV"],
            rank=2,
        )
    )

    assert session.role_title == "Transformation Lead"
    assert session.candidate_count == 2
    assert session.analyzed_count == 1
    assert session.error_count == 1
    assert session.get_analysis("Alice").match_score == 90
