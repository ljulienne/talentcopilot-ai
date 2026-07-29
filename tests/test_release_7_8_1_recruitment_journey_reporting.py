from pathlib import Path

from talentcopilot.models.hiring_budget import HiringBudgetInput
from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.compensation_budget_service import (
    CandidateCompensationExpectation,
    CompensationBudgetService,
)
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.hiring_budget_service import HiringBudgetService
from talentcopilot.services.recruitment_overview_service import RecruitmentOverviewService
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService
from talentcopilot.services.recruitment_workflow_state import get_workflow_context
from talentcopilot.ui.brand import brand_lockup_html
from talentcopilot.ui.enterprise_navigation import get_page_by_label
from talentcopilot.ui.premium_sidebar import (
    RECRUITMENT_JOURNEY_LABELS,
    resolve_recruitment_destinations,
)
from talentcopilot.ui.recruitment_workflow_shell import aggregate_workflow_steps
from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService


ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
DASHBOARD_SOURCE = (ROOT / "talentcopilot/ui/recruitment_overview.py").read_text(encoding="utf-8")
CANDIDATE_SOURCE = (ROOT / "talentcopilot/ui/candidate_workspace.py").read_text(encoding="utf-8")
INTERVIEW_SOURCE = (ROOT / "talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")
COMPARISON_SOURCE = (ROOT / "talentcopilot/ui/comparison_workspace.py").read_text(encoding="utf-8")
COMPENSATION_SOURCE = (ROOT / "talentcopilot/ui/hiring_budget.py").read_text(encoding="utf-8")
MISSION_SOURCE = (ROOT / "talentcopilot/recruitment/mission/workspace.py").read_text(encoding="utf-8")


def _session():
    return RecruitmentSession(
        session_id="release-781",
        job={"title": "HRIS Manager"},
        candidates=[
            {"candidate_id": "alice", "name": "Alice"},
            {"candidate_id": "bob", "name": "Bob"},
        ],
        status=SessionStatus.COMPLETED,
        analyses=[
            CandidateAnalysisState(
                candidate_name="Alice",
                candidate_id="alice",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=82,
                rank=1,
                score_breakdown={"confidence": 88},
            ),
            CandidateAnalysisState(
                candidate_name="Bob",
                candidate_id="bob",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=68,
                rank=2,
                score_breakdown={"confidence": 76},
            ),
        ],
    )


def test_sidebar_exposes_complete_recruitment_journey_and_home():
    items = resolve_recruitment_destinations(
        _session(),
        current_page="Dashboard Perspective",
        include_journey_v2=True,
    )
    assert tuple(item.label for item in items) == RECRUITMENT_JOURNEY_LABELS
    assert "Home" in (ROOT / "talentcopilot/ui/premium_sidebar.py").read_text(encoding="utf-8")
    assert "tc_page=Executive%20Brief" in brand_lockup_html()


def test_primary_routes_separate_overview_dashboard_and_contextual_candidate_detail():
    assert get_page_by_label("Recruitment Overview").module == "talentcopilot.ui.recruitment_decision_workspace"
    assert get_page_by_label("Dashboard Perspective").module == "talentcopilot.ui.recruitment_overview"
    assert get_page_by_label("Compensation & Budget").module == "talentcopilot.ui.hiring_budget"
    assert get_page_by_label("Candidate Intelligence").module == "talentcopilot.ui.candidate_workspace"


def test_workflow_strip_is_sticky_top_and_includes_transversal_compensation():
    session = _session()
    context = get_workflow_context(session, current_page="Compensation & Budget")
    states = RecruitmentWorkflowService().resolve_steps(
        session,
        context,
        current_page="Compensation & Budget",
    )
    groups = aggregate_workflow_steps(
        states,
        current_page="Compensation & Budget",
        session=session,
    )
    assert [item.key for item in groups] == ["analyze", "review", "compensation", "interview", "decide"]
    assert next(item for item in groups if item.key == "compensation").current is True
    source = (ROOT / "talentcopilot/ui/recruitment_workflow_shell.py").read_text(encoding="utf-8")
    assert "position:sticky" in source
    assert "linear-gradient(90deg,#1D4ED8" in source
    assert '"Dashboard Perspective"' in APP_SOURCE
    assert '"Compensation & Budget"' in APP_SOURCE


def test_compensation_persistence_never_changes_official_scores_or_ranks():
    session = _session()
    scores_before = [(item.match_score, item.rank) for item in session.analyses]
    service = CompensationBudgetService()
    budget = HiringBudgetInput(
        target_salary=85000,
        maximum_salary=100000,
        minimum_salary=70000,
        currency="EUR",
        first_year_cost_limit=120000,
    )
    service.save_budget(session, budget)
    service.save_expectation(
        session,
        CandidateCompensationExpectation(
            candidate_id="alice",
            candidate_name="Alice",
            expected_salary=92000,
            variable_compensation=8000,
            benefits_requested="Remote work and health coverage",
            notice_period_weeks=8,
            flexibility="Moderate",
        ),
    )
    report = HiringBudgetService().build(session, service.load_budget(session))
    assert report.assessments[0].expected_salary == 92000
    assert report.assessments[0].budget_fit is not None
    assert service.documented_count(session) == 1
    assert [(item.match_score, item.rank) for item in session.analyses] == scores_before


def test_all_recruitment_spaces_restore_visible_pdf_exports():
    assert "Download recruitment overview (PDF)" in MISSION_SOURCE
    assert "Download candidate perspective (PDF)" in DASHBOARD_SOURCE
    assert "Download candidate report (PDF)" in CANDIDATE_SOURCE
    assert "Download interview report (PDF)" in INTERVIEW_SOURCE
    assert "Download decision report (PDF)" in COMPARISON_SOURCE
    assert "Download compensation report (PDF)" in COMPENSATION_SOURCE


def test_pdf_service_generates_valid_dashboard_and_compensation_documents():
    session = create_demo_recruitment_session()
    context = get_workflow_context(session, current_page="Dashboard Perspective")
    view = RecruitmentOverviewService().build(session, context)
    compensation_service = CompensationBudgetService()
    budget = compensation_service.load_budget(session)
    compensation_report = HiringBudgetService().build(session, budget)
    pdf_service = RecruitmentPdfService()
    dashboard = pdf_service.dashboard(view, compensation_report)
    compensation = pdf_service.compensation(
        compensation_report,
        budget,
        compensation_service.all_expectations(session),
    )
    assert dashboard.data.startswith(b"%PDF")
    assert compensation.data.startswith(b"%PDF")
    assert dashboard.file_name.endswith(".pdf")
    assert compensation.file_name.endswith(".pdf")


def test_dashboard_is_the_post_analysis_destination_and_opens_candidate_detail():
    assert 'request_page(\n            "Dashboard Perspective"' in MISSION_SOURCE
    assert "_candidate_cards(view, compensation_report)" in DASHBOARD_SOURCE
    assert 'request_page(\n                        "Candidate Intelligence"' in DASHBOARD_SOURCE
    assert "dashboard_perspective_filter" in DASHBOARD_SOURCE
    assert "dashboard_perspective_sort" in DASHBOARD_SOURCE
    assert "← Back to Dashboard Perspective" in CANDIDATE_SOURCE


def test_sidebar_contrast_is_strengthened_and_primary_actions_remain_non_red():
    assert "color:#EEF4FC" in THEME_SOURCE
    assert "font-weight:760" in THEME_SOURCE
    assert "font-size:.89rem" in THEME_SOURCE
    primary_rule = THEME_SOURCE.rsplit('.stButton > button[kind="primary"]', 1)[1].split("}}", 1)[0]
    assert "red" not in primary_rule.lower()
    assert "#B91C1C" not in primary_rule


def test_compensation_is_available_before_and_after_interview():
    assert "Candidate expectations" in COMPENSATION_SOURCE
    assert "Offer scenarios" in COMPENSATION_SOURCE
    assert "availability_date" in COMPENSATION_SOURCE
    assert "benefits_requested" in COMPENSATION_SOURCE
    assert "Record compensation" in INTERVIEW_SOURCE
    assert "Review Compensation & Budget" in COMPARISON_SOURCE
