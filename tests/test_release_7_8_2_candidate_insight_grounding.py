from pathlib import Path
from types import SimpleNamespace

from talentcopilot.models.candidate_workspace import CandidateRisk, CandidateSkill
from talentcopilot.models.competency_matrix import CandidateCompetencyMatrix, CompetencyAssessment
from talentcopilot.services.recruitment_overview_service import RecruitmentOverviewService
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_SOURCE = (ROOT / "talentcopilot/ui/recruitment_overview.py").read_text(encoding="utf-8")


def _competency(name: str, *, required: float, estimated: float) -> CompetencyAssessment:
    return CompetencyAssessment(
        competency_id=name.lower().replace(" ", "-"),
        competency_name=name,
        category="Role requirement",
        importance="Required",
        required_level=required,
        ai_estimated_level=estimated,
        confidence="Moderate",
        evidence_status="Candidate evidence",
        evidence=f"Evidence for {name}",
        origin="job_requirement",
    )


def _matrix(candidate_name: str) -> CandidateCompetencyMatrix:
    # SAP is intentionally first to reproduce the 7.8.1 regression. The
    # dashboard must not reuse this ordering as a candidate insight.
    return CandidateCompetencyMatrix(
        candidate_id=candidate_name.lower(),
        candidate_name=candidate_name,
        job_id="job-782",
        role_title="HRIS Manager",
        competencies=[
            _competency("SAP SuccessFactors", required=4, estimated=2),
            _competency("Stakeholder leadership", required=4, estimated=3),
            _competency("Data governance", required=4, estimated=2.5),
        ],
    )


class _CandidateService:
    def build_all(self, session):
        return list(session.reports)


class _CompetencyService:
    def build(self, report, session):
        return _matrix(report.candidate_name)


class _TiedCompetencyService:
    def build(self, report, session):
        return CandidateCompetencyMatrix(
            candidate_id=report.candidate_id,
            candidate_name=report.candidate_name,
            job_id="job-782-tied",
            role_title="HRIS Manager",
            competencies=[
                _competency("SAP SuccessFactors", required=4, estimated=2),
                _competency("Stakeholder leadership", required=4, estimated=2),
            ],
        )


def _report(name, candidate_id, score, rank, skills, risks):
    return SimpleNamespace(
        candidate_name=name,
        candidate_id=candidate_id,
        match_score=score,
        rank=rank,
        score_breakdown={"confidence": 91 - rank},
        recommendation_label="Proceed with validation",
        recommendation="Proceed with validation",
        skills=skills,
        risks=risks,
    )


def _session(*reports):
    return SimpleNamespace(
        session_id="release-782",
        role_title="HRIS Manager",
        candidate_count=len(reports),
        analyzed_count=len(reports),
        reports=reports,
    )


def test_dashboard_insights_are_grounded_per_candidate_and_preserve_official_order():
    louis = _report(
        "Louis Julienne",
        "louis",
        85,
        1,
        [
            CandidateSkill("SAP SuccessFactors", 58, requirement_type="Role requirement"),
            CandidateSkill("Stakeholder leadership", 91, status="Strong evidence", requirement_type="Role requirement"),
        ],
        [
            CandidateRisk(
                title="Data governance requires validation",
                detail="Limited governance evidence.",
                severity="High",
                related_requirement="Data governance",
            )
        ],
    )
    vincent = _report(
        "Vincent Blakoe",
        "vincent",
        81,
        2,
        [
            CandidateSkill("SAP SuccessFactors", 94, status="Strong evidence", requirement_type="Role requirement"),
            CandidateSkill("Stakeholder leadership", 74, requirement_type="Role requirement"),
        ],
        [
            CandidateRisk(
                title="Measurable impact is not established",
                detail="Outcomes need quantification.",
                severity="Medium",
                related_requirement="Demonstrated delivery impact",
            )
        ],
    )
    service = RecruitmentOverviewService(
        candidate_service=_CandidateService(),
        competency_service=_CompetencyService(),
    )
    view = service.build(_session(louis, vincent))

    assert [(item.official_match_score, item.official_rank) for item in view.candidates] == [
        (85.0, 1),
        (81.0, 2),
    ]
    assert view.candidates[0].strongest_area == "Stakeholder leadership"
    assert view.candidates[0].primary_risk == "Data governance requires validation"
    assert view.candidates[1].strongest_area == "SAP SuccessFactors"
    assert view.candidates[1].primary_risk == "Measurable impact is not established"
    assert len({item.strongest_area for item in view.candidates}) == 2
    assert len({item.primary_risk for item in view.candidates}) == 2


def test_primary_risk_uses_the_highest_priority_grounded_risk_title():
    report = _report(
        "Alice",
        "alice",
        78,
        1,
        [CandidateSkill("Programme leadership", 92, status="Strong evidence", requirement_type="Role requirement")],
        [
            CandidateRisk(
                title="Programme leadership requires validation",
                detail="Validate scale.",
                severity="High",
                related_requirement="Programme leadership",
            ),
            CandidateRisk(
                title="Commercial ownership is unclear",
                detail="Validate budget accountability.",
                severity="Medium",
                related_requirement="Commercial ownership",
            ),
        ],
    )
    service = RecruitmentOverviewService(
        candidate_service=_CandidateService(),
        competency_service=_CompetencyService(),
    )
    candidate = service.build(_session(report)).candidates[0]

    assert candidate.strongest_area == "Programme leadership"
    assert candidate.primary_risk == "Programme leadership requires validation"
    assert candidate.primary_risk != candidate.strongest_area


def test_no_first_requirement_fallback_when_evidence_is_not_differentiated():
    report = _report(
        "Uncertain Candidate",
        "uncertain",
        50,
        1,
        [
            CandidateSkill("SAP SuccessFactors", 35, status="Limited evidence", requirement_type="Role requirement"),
            CandidateSkill("Stakeholder leadership", 35, status="Limited evidence", requirement_type="Role requirement"),
        ],
        [],
    )
    service = RecruitmentOverviewService(
        candidate_service=_CandidateService(),
        competency_service=_TiedCompetencyService(),
    )
    candidate = service.build(_session(report)).candidates[0]

    assert candidate.strongest_area == "No differentiated strength established"
    assert candidate.primary_risk.endswith("requires validation")


def test_dashboard_ui_and_pdf_use_the_grounded_fields():
    assert "candidate.strongest_area" in DASHBOARD_SOURCE
    assert "candidate.primary_risk" in DASHBOARD_SOURCE
    assert "competency_scores_post[0]" not in DASHBOARD_SOURCE
    assert "critical_gaps[0]" not in DASHBOARD_SOURCE

    report = _report(
        "PDF Candidate",
        "pdf",
        72,
        1,
        [CandidateSkill("Change leadership", 86, status="Strong evidence", requirement_type="Role requirement")],
        [
            CandidateRisk(
                title="Analytics depth requires validation",
                detail="Validate technical depth.",
                severity="Medium",
                related_requirement="Analytics depth",
            )
        ],
    )
    service = RecruitmentOverviewService(
        candidate_service=_CandidateService(),
        competency_service=_CompetencyService(),
    )
    view = service.build(_session(report))
    pdf = RecruitmentPdfService().dashboard(view)

    assert pdf.data.startswith(b"%PDF")
    assert view.candidates[0].strongest_area == "Change leadership"
    assert view.candidates[0].primary_risk == "Analytics depth requires validation"
