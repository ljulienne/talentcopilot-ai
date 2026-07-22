from types import SimpleNamespace

from talentcopilot.models.candidate_workspace import CandidateSkill, CandidateWorkspaceReport
from talentcopilot.services.competency_matrix_service import CompetencyMatrixService


def _report(name="Louis Julienne", candidate_id="louis"):
    return CandidateWorkspaceReport(
        candidate_name=name,
        candidate_id=candidate_id,
        rank=1,
        match_score=78.0,
        recommendation="Proceed with validation",
        executive_summary="Strong profile.",
        skills=[
            CandidateSkill("Project Management", 84, "Led a regional transformation.", "Strong evidence", "High", "Role requirement"),
            CandidateSkill("SAP SuccessFactors", 46, "SAP exposure requires validation.", "Limited evidence", "Limited", "Role requirement"),
            CandidateSkill("Budget Management", 74, "Managed a regional budget.", "Moderate evidence", "Moderate", "Role requirement"),
        ],
    )


def _session():
    return SimpleNamespace(session_id="job-1", role_title="HRIS Manager", job={"title": "HRIS Manager"})


def test_matrix_uses_distinct_skill_levels_and_preserves_official_result(tmp_path):
    report = _report()
    service = CompetencyMatrixService(tmp_path)
    matrix = service.build(report, _session())
    values = {item.competency_name: item.ai_estimated_level for item in matrix.competencies}
    assert values["Project Management"] == 4.2
    assert values["SAP SuccessFactors"] == 2.3
    assert report.match_score == 78.0
    assert report.rank == 1


def test_interview_update_preserves_ai_estimate_and_creates_audit_history(tmp_path):
    service = CompetencyMatrixService(tmp_path)
    matrix = service.build(_report(), _session())
    skill = matrix.competencies[0]
    original = skill.ai_estimated_level
    service.update(matrix, {skill.competency_id: {"interviewer_level": 4.8, "validation_status": "Confirmed", "comment": "Strong example."}}, evaluator="Recruiter")
    assert skill.ai_estimated_level == original
    assert skill.interviewer_level == 4.8
    assert skill.consolidated_level is not None
    assert matrix.audit_history
    loaded = service.load("louis", "job-1")
    assert loaded is not None
    assert loaded.competencies[0].validation_status == "Confirmed"


def test_comparison_rows_align_candidates_by_competency(tmp_path):
    service = CompetencyMatrixService(tmp_path)
    first = service.build(_report(), _session())
    second = service.build(_report("Vincent Blakoe", "vincent"), _session())
    second.competencies[0].consolidated_level = 3.7
    rows = service.comparison_rows([first, second])
    project = next(row for row in rows if row["Competency"] == "Project Management")
    assert project["Louis Julienne"] == 4.2
    assert project["Vincent Blakoe"] == 3.7
