from pathlib import Path

from talentcopilot.interview.models import InterviewCompetency
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.competency_matrix_service import CompetencyMatrixService
from talentcopilot.services.recruitment_overview_service import RecruitmentOverviewService
from talentcopilot.technical_requirements import TechnicalRequirementService


JOB_TEXT = """
HRIS MANAGER
Lead and coordinate complex HRIS projects including interfaces with third-party systems.
Support deployment of Core HR. Participate actively in the development of Artificial
Intelligence (AI) solutions aimed at optimizing HR processes. Provide expertise on SAP
SuccessFactors. Carry out data cleaning and data reliability actions within Core HR.
Design and implement dynamic Power BI reports from Core HR data. Ensure functional
and technical acceptance testing. Support adoption through communication and training.
Manage HRIS solution providers and integrators. Manage an internal collaborator.
Minimum 10 years of HRIS project management in an international environment.
"""

LOUIS_TEXT = """
Global HR professional with 10+ years of international HRIS experience.
Implemented SeditWeb2 HRIS and integrated it with Octime.
Delivered HR analytics through Business Objects.
Implemented TAPPLENT HRIS, Premium RH and payroll systems.
Created Tableau dashboards. Launched Microsoft Power BI for China HR Teams and
ensured HR data accuracy, integrity and GDPR compliance. Managed SIT/UAT in China.
IBM Data Science Professional Certificate. Python notions. Liaised with vendors.
"""


def _session() -> RecruitmentSession:
    return RecruitmentSession(
        session_id="technical-760",
        job={
            "job_id": "job-hris",
            "title": "HRIS Manager",
            "raw_text": JOB_TEXT,
            "required_skills": ["HRIS", "Project Management", "Reporting"],
        },
        candidates=[
            {
                "candidate_id": "louis",
                "name": "Louis Julienne",
                "skills": ["HRIS", "Project Management", "Power BI", "Data Analysis"],
                "achievements": [
                    "Launched Microsoft Power BI for China HR Teams.",
                    "Implemented SeditWeb2 HRIS and integrated it with Octime.",
                ],
                "raw_text": LOUIS_TEXT,
                "years_experience": 10,
            },
            {
                "candidate_id": "other",
                "name": "Other Candidate",
                "skills": ["HRIS"],
                "achievements": [],
                "raw_text": "HRIS project support and reporting.",
                "years_experience": 5,
            },
        ],
        analyses=[
            CandidateAnalysisState(
                candidate_id="louis",
                candidate_name="Louis Julienne",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=82,
                rank=1,
            ),
            CandidateAnalysisState(
                candidate_id="other",
                candidate_name="Other Candidate",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=51,
                rank=2,
            ),
        ],
        status=SessionStatus.COMPLETED,
    )


def test_job_catalog_preserves_exact_technical_requirements():
    catalog = TechnicalRequirementService().catalog(
        {"title": "HRIS Manager", "raw_text": JOB_TEXT}
    )
    names = [item.name for item in catalog.requirements]

    assert names[:3] == [
        "SAP SuccessFactors & Core HR",
        "Power BI & HR Reporting",
        "AI Solutions for HR",
    ]
    assert "Interfaces & Technical Delivery" in names
    assert "Data Quality & Core HR Reliability" in names
    assert len(names) <= 9


def test_candidate_evidence_distinguishes_direct_related_and_missing():
    service = TechnicalRequirementService()
    catalog = service.catalog({"title": "HRIS Manager", "raw_text": JOB_TEXT})
    candidate = {"raw_text": LOUIS_TEXT, "skills": ["Power BI", "HRIS"]}
    evidence = {
        item.name: service.evaluate_candidate(item, candidate)
        for item in catalog.requirements
    }

    assert evidence["Power BI & HR Reporting"].evidence_status == "Direct evidence"
    assert evidence["Power BI & HR Reporting"].estimated_level >= 3.0
    assert evidence["SAP SuccessFactors & Core HR"].evidence_status == "Related evidence"
    assert "tapplent" in " ".join(evidence["SAP SuccessFactors & Core HR"].related_evidence).lower()
    assert evidence["AI Solutions for HR"].evidence_status == "Related evidence"
    assert evidence["AI Solutions for HR"].interview_priority in {
        "Mandatory probe", "Validate transferability"
    }


def test_radar_uses_unified_exact_requirements(tmp_path):
    session = _session()
    report = RecruitmentOverviewService(
        competency_service=CompetencyMatrixService(storage_dir=tmp_path / "matrices")
    ).candidate_service.build_all(session)[0]
    matrix = CompetencyMatrixService(storage_dir=tmp_path / "matrices").build(report, session)
    active = {item.competency_name: item for item in matrix.active_competencies()}

    assert "SAP SuccessFactors & Core HR" in active
    assert "Power BI & HR Reporting" in active
    assert "AI Solutions for HR" in active
    assert active["Power BI & HR Reporting"].evidence_status == "Direct evidence"
    assert active["SAP SuccessFactors & Core HR"].evidence_status == "Related evidence"
    assert active["SAP SuccessFactors & Core HR"].interview_priority == "Mandatory probe"


def test_interview_questions_probe_successfactors_power_bi_and_ai():
    session = _session()
    reports = InterviewWorkspaceService().build_all(session)
    louis = reports[0]
    by_name = {item.competency: item for item in louis.questions}

    assert "SAP SuccessFactors & Core HR" in by_name
    assert "Power BI & HR Reporting" in by_name
    assert "AI Solutions for HR" in by_name
    assert "transferable" in by_name["SAP SuccessFactors & Core HR"].question.lower()
    assert "dax" in by_name["Power BI & HR Reporting"].question.lower()
    assert "bias" in by_name["AI Solutions for HR"].question.lower()


def test_pool_coverage_is_the_average_of_heatmap_values(tmp_path):
    session = _session()
    service = RecruitmentOverviewService(
        competency_service=CompetencyMatrixService(storage_dir=tmp_path / "matrices")
    )
    view = service.build(session)
    coverage = {item.competency: item for item in view.competency_coverage}

    for competency, row in coverage.items():
        values = [
            dict(candidate.competency_scores_pre)[competency]
            for candidate in view.candidates
            if competency in dict(candidate.competency_scores_pre)
        ]
        assert row.pre_interview_coverage == round(sum(values) / len(values))


def test_official_scores_and_ranks_remain_immutable(tmp_path):
    session = _session()
    before = [(item.match_score, item.rank) for item in session.analyses]
    RecruitmentOverviewService(
        competency_service=CompetencyMatrixService(storage_dir=tmp_path / "matrices")
    ).build(session)
    InterviewWorkspaceService().build_all(session)
    assert [(item.match_score, item.rank) for item in session.analyses] == before
