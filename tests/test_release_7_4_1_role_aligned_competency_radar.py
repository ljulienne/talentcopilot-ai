from types import SimpleNamespace
from pathlib import Path

from talentcopilot.models.candidate_workspace import CandidateSkill, CandidateWorkspaceReport
from talentcopilot.services.competency_matrix_service import CompetencyMatrixService
from talentcopilot.ui.competency_star import (
    build_competency_star_data,
    build_competency_star_figure,
)


def _report():
    return CandidateWorkspaceReport(
        candidate_name="Alice Martin",
        candidate_id="alice",
        rank=1,
        match_score=78.0,
        recommendation="Proceed",
        executive_summary="Strong profile.",
        skills=[
            CandidateSkill(
                "Project Management",
                80,
                "Led a transformation.",
                "Strong evidence",
                "High",
                "Role requirement",
            ),
            CandidateSkill(
                "Change Management",
                45,
                "Limited change evidence.",
                "Limited evidence",
                "Limited",
                "Role requirement",
            ),
            CandidateSkill(
                "Photography",
                90,
                "Personal portfolio.",
                "Strong evidence",
                "High",
                "Additional capability",
            ),
        ],
    )


def _session():
    return SimpleNamespace(
        session_id="job-42",
        role_title="Transformation Lead",
        job={
            "title": "Transformation Lead",
            "required_skills": ["Project Management", "Change Management"],
        },
    )


def test_matrix_axes_come_only_from_job_requirements(tmp_path):
    matrix = CompetencyMatrixService(tmp_path).build(_report(), _session())
    names = [item.competency_name for item in matrix.active_competencies()]
    assert names == ["Project Management", "Change Management"]
    assert "Photography" not in names
    assert all(item.origin == "job_requirement" for item in matrix.competencies)


def test_radar_compares_role_expectation_and_pre_interview_estimate(tmp_path):
    matrix = CompetencyMatrixService(tmp_path).build(_report(), _session())
    data = build_competency_star_data(matrix.active_competencies())
    assert data["required"] == [80, 80]
    assert data["pre_interview"] == [80, 45]
    assert data["has_required_profile"] is True
    assert len(build_competency_star_figure(data).data) == 2


def test_post_interview_profile_preserves_ai_estimate(tmp_path):
    service = CompetencyMatrixService(tmp_path)
    matrix = service.build(_report(), _session())
    competency = matrix.competencies[0]
    original_ai = competency.ai_estimated_level

    service.update(
        matrix,
        {
            competency.competency_id: {
                "interviewer_level": 4.8,
                "validation_status": "Confirmed",
                "comment": "Strong quantified evidence.",
                "interview_evidence": "I led the programme across twelve countries.",
            }
        },
        evaluator="Recruiter",
    )

    assert competency.ai_estimated_level == original_ai
    assert competency.interview_evidence == "I led the programme across twelve countries."
    data = build_competency_star_data(matrix.active_competencies())
    assert data["has_post_interview"] is True
    assert data["post_interview"][0] == 96
    assert len(build_competency_star_figure(data).data) == 3


def test_interview_added_competency_can_be_renamed_removed_and_restored(tmp_path):
    service = CompetencyMatrixService(tmp_path)
    matrix = service.build(_report(), _session())
    required = matrix.competencies[0]
    assert service.remove_competency(matrix, required.competency_id, evaluator="Recruiter") is False

    added = service.add_competency(
        matrix,
        "Vendor Management",
        evaluator="Recruiter",
        interviewer_level=4.0,
    )
    assert added.origin == "interview_added"
    assert added.required_level == 0.0
    assert service.rename_competency(
        matrix,
        added.competency_id,
        "Strategic Vendor Management",
        evaluator="Recruiter",
    ) is True
    assert service.remove_competency(
        matrix,
        added.competency_id,
        evaluator="Recruiter",
    ) is True
    assert added.is_active is False
    assert service.restore_competency(
        matrix,
        added.competency_id,
        evaluator="Recruiter",
    ) is True
    assert added.is_active is True


def test_final_radar_is_versioned_and_persisted(tmp_path):
    service = CompetencyMatrixService(tmp_path)
    matrix = service.build(_report(), _session())
    service.update(
        matrix,
        {
            matrix.competencies[0].competency_id: {
                "interviewer_level": 4.5,
                "validation_status": "Confirmed",
            }
        },
        evaluator="Recruiter",
    )
    service.finalize(matrix, evaluator="Recruiter")

    loaded = service.load("alice", "job-42")
    assert loaded is not None
    assert loaded.status == "post_interview"
    assert loaded.finalized_by == "Recruiter"
    assert loaded.finalized_at
    assert list((Path(tmp_path) / "history").glob("*__v*.json"))


def test_candidate_workspace_is_read_only_and_interview_owns_editing():
    candidate_source = Path("talentcopilot/ui/candidate_workspace.py").read_text(encoding="utf-8")
    interview_source = Path("talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")

    assert "Open Interview Intelligence to evaluate" in candidate_source
    assert "Save competency assessment" not in candidate_source
    assert "Add to competency radar" in interview_source
    assert "Remove competency" in interview_source
    assert "post_interview_radar" in interview_source
