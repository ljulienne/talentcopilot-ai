from types import SimpleNamespace

from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.recruitment.mission.state import build_recruitment_mission_state
from talentcopilot.recruitment_source_of_truth.models import OfficialCandidateRecord, RecruitmentSourceOfTruth


def _analysis(candidate_id, name, score, rank, rationale):
    return SimpleNamespace(
        candidate_id=candidate_id,
        candidate_name=name,
        match_score=score,
        rank=rank,
        official_rank=rank,
        official_match_score=score,
        official_decision_score=score,
        official_confidence_score=80,
        score_breakdown={"mission_fit_rank": rank, "decision_rank": rank},
        decision_score=score,
        notes=[rationale, "Recommendation: Interview"],
        errors=[],
    )


def _session():
    louis = _analysis("louis", "Louis Julienne", 84, 1, "Louis Julienne: 84% evidence-led Mission Fit.")
    vincent = _analysis(
        "vincent",
        "Vincent Blakoe",
        77,
        2,
        "Credit Suisse: 77% evidence-led Mission Fit. No evidence found for Change Management; No evidence found for Reporting and analytics.",
    )
    return SimpleNamespace(
        session_id="session-702",
        role_title="HRIS Manager",
        status="analyzed",
        candidate_count=2,
        analyzed_count=2,
        ranked_analyses=[vincent, louis],  # deliberately wrong storage order
        analyses=[vincent, louis],
        candidates=[
            {"candidate_id": "louis", "name": "Louis Julienne", "skills": ["HRIS"], "achievements": ["Led an HRIS deployment across APAC"]},
            {"candidate_id": "vincent", "name": "Vincent Blakoe", "skills": ["HRIS"], "achievements": ["Managed HR systems projects"]},
        ],
        job={"title": "HRIS Manager", "required_skills": ["HRIS", "Change Management", "Reporting and analytics"]},
        metadata={
            "recruitment_source_of_truth": RecruitmentSourceOfTruth(
                session_id="session-702",
                role_title="HRIS Manager",
                version="recruitment-sot-v1.0",
                candidates=[
                    OfficialCandidateRecord(
                        candidate_id="vincent", candidate_name="Vincent Blakoe", mission_fit_score=77,
                        decision_score=77, mission_rank=2, decision_rank=2, interview_priority=1,
                    ),
                    OfficialCandidateRecord(
                        candidate_id="louis", candidate_name="Louis Julienne", mission_fit_score=84,
                        decision_score=84, mission_rank=1, decision_rank=1, interview_priority=2,
                    ),
                ],
                analysis_fingerprint="test",
            ).to_dict()
        },
    )


def test_interview_reports_follow_official_mission_rank_not_interview_priority():
    reports = InterviewWorkspaceService().build_all(_session())
    assert [(item.official_rank, item.candidate_name) for item in reports] == [
        (1, "Louis Julienne"),
        (2, "Vincent Blakoe"),
    ]


def test_mission_state_uses_canonical_identity_and_candidate_specific_validation_focus():
    state = build_recruitment_mission_state(_session())
    vincent = next(item for item in state.candidates if item.candidate_id == "vincent")
    louis = next(item for item in state.candidates if item.candidate_id == "louis")

    assert vincent.rationale.startswith("Vincent Blakoe: 77%")
    assert not vincent.rationale.startswith("Credit Suisse:")
    assert any("Change Management" in item for item in vincent.validation_focus)
    assert any("Reporting and analytics" in item for item in vincent.validation_focus)
    assert vincent.validation_focus != louis.validation_focus
    assert all("Validate the strongest claims" not in item for item in vincent.validation_focus)
