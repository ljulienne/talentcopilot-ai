from types import SimpleNamespace

from talentcopilot.services.recruitment_cockpit_service import (
    RecruitmentCockpitService,
)


def _analysis(name: str, score: float, rank: int):
    return SimpleNamespace(
        candidate_name=name,
        match_score=score,
        rank=rank,
    )


def test_cockpit_uses_official_ranked_analyses_without_recalculation():
    session = SimpleNamespace(
        session_id="session-321",
        role_title="HRIS Project Manager",
        candidate_count=3,
        analyzed_count=3,
        ranked_analyses=[
            _analysis("Candidate B", 71.0, 2),
            _analysis("Candidate A", 84.0, 1),
            _analysis("Candidate C", 55.0, 3),
        ],
    )
    report = SimpleNamespace(
        role_title="HRIS Project Manager",
        session_id="session-321",
        candidates_count=3,
        analyzed_count=3,
    )

    view = RecruitmentCockpitService().build(session, report)

    assert view.top_candidate_name == "Candidate A"
    assert view.top_candidate_score == 84.0
    assert view.candidates_count == 3
    assert view.analyzed_count == 3
    assert view.next_action_title == "Review Candidate A"


def test_cockpit_workflow_is_guided_and_deterministic():
    session = SimpleNamespace(
        session_id="session-321",
        role_title="HRIS Project Manager",
        candidate_count=2,
        analyzed_count=2,
        ranked_analyses=[_analysis("Candidate A", 84.0, 1)],
    )
    report = SimpleNamespace(
        role_title="HRIS Project Manager",
        session_id="session-321",
        candidates_count=2,
        analyzed_count=2,
    )

    view = RecruitmentCockpitService().build(session, report)

    assert [step.label for step in view.workflow_steps] == [
        "Mission",
        "Candidates",
        "AI Analysis",
        "Interview",
        "Decision",
    ]
    assert [step.status for step in view.workflow_steps[:3]] == [
        "done",
        "done",
        "done",
    ]
    assert view.workflow_steps[3].status == "active"
    assert view.progress_percent == 60
    assert view.current_stage == "Interview"


def test_empty_cockpit_recommends_mission_definition():
    session = SimpleNamespace(
        session_id="session-empty",
        role_title="Recruitment",
        candidate_count=0,
        analyzed_count=0,
        ranked_analyses=[],
    )
    report = SimpleNamespace(
        role_title="No active recruitment",
        session_id="session-empty",
        candidates_count=0,
        analyzed_count=0,
    )

    view = RecruitmentCockpitService().build(session, report)

    assert view.progress_percent == 0
    assert view.current_stage == "Mission"
    assert view.next_action_title == "Define the mission"
