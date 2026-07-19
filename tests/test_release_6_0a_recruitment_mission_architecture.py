from talentcopilot.models.recruitment_session import CandidateAnalysisState, CandidateAnalysisStatus, RecruitmentSession, SessionStatus
from talentcopilot.recruitment.mission.navigation import MISSION_SECTIONS
from talentcopilot.recruitment.mission.state import build_recruitment_mission_state
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def _session():
    return RecruitmentSession(
        session_id="release-60a",
        job={"title": "Senior Sales Manager APAC"},
        candidates=[
            {"candidate_id": "john", "name": "John", "achievements": ["Regional APAC sales leadership"], "upload_recommendation": "Strong shortlist", "upload_rationale": "Broadest regional scope."},
            {"candidate_id": "sarah", "name": "Sarah", "achievements": ["Textile commercial leadership"], "upload_recommendation": "Strong shortlist", "upload_rationale": "Strong alternative."},
        ],
        status=SessionStatus.COMPLETED,
        analyses=[
            CandidateAnalysisState(candidate_name="John", candidate_id="john", status=CandidateAnalysisStatus.ANALYZED, match_score=96, decision_score=91, rank=1, score_breakdown={"confidence": 88}),
            CandidateAnalysisState(candidate_name="Sarah", candidate_id="sarah", status=CandidateAnalysisStatus.ANALYZED, match_score=82, decision_score=80, rank=2, score_breakdown={"confidence": 86}),
        ],
    )


def test_mission_state_preserves_official_scores_and_ranks():
    state = build_recruitment_mission_state(_session())
    assert [(item.name, item.rank, item.match_score) for item in state.candidates] == [
        ("John", 1, 96.0),
        ("Sarah", 2, 82.0),
    ]
    assert state.recommended_candidate == "John"
    assert state.average_confidence == 87.0


def test_mission_architecture_has_decision_led_sections():
    assert [section.key for section in MISSION_SECTIONS] == [
        "overview", "ranking", "reasoning", "comparison", "interview", "decision", "report"
    ]
    assert all(section.question for section in MISSION_SECTIONS)


def test_primary_navigation_keeps_stable_compatibility_entrypoint():
    page = get_page_by_label("Recruitment Workspace")
    assert page.module == "talentcopilot.ui.recruitment_decision_workspace"
    assert page.function == "render_recruitment_decision_workspace"


def test_workspace_imports_without_streamlit_execution():
    module = __import__(
        "talentcopilot.recruitment.mission.workspace",
        fromlist=["render_recruitment_mission_workspace"],
    )
    assert hasattr(module, "render_recruitment_mission_workspace")
