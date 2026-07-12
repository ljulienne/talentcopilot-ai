from talentcopilot.interview.models import InterviewCompetency
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_active_interview_route_uses_session_based_page():
    page = get_page_by_label("Interview Intelligence")
    assert page is not None
    assert page.module == "talentcopilot.ui.interview_intelligence"
    assert page.function == "render_interview_intelligence"

    source = __import__(page.module, fromlist=[page.function])
    assert hasattr(source, page.function)


def test_interview_reports_preserve_official_scores_and_ranks_context():
    session = create_demo_recruitment_session()
    reports = InterviewWorkspaceService().build_all(session)
    reports_by_name = {report.candidate_name: report for report in reports}

    for analysis in session.ranked_analyses:
        assert reports_by_name[analysis.candidate_name].fit_score == analysis.match_score


def test_questions_are_specific_and_not_the_old_generic_template():
    competency = InterviewCompetency(
        name="Stakeholder Management",
        evidence_level="Low",
        confidence=38,
        validate_in_interview=True,
        rationale="The mission requires stakeholder management but direct ownership is not evidenced.",
    )
    questions = InterviewQuestionService().build(
        [competency],
        role_title="International HRIS Program Manager",
        candidate={
            "years_experience": 13,
            "achievements": [
                "Led international HRIS deployments for multiple banking and pharmaceutical clients."
            ],
        },
        mission_requirements=["Stakeholder Management"],
    )

    assert len(questions) == 1
    question = questions[0]
    assert "Tell me about a concrete situation" not in question.question
    assert "International HRIS Program Manager" in question.question
    assert "personally" in question.question
    assert "measurable" in question.question
    assert len(question.follow_ups) >= 3
    assert any("ownership" in item.lower() for item in question.positive_signals)


def test_interview_ui_does_not_use_demo_ranking_service():
    from pathlib import Path
    import talentcopilot.ui.interview_intelligence as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "RealRankingDemoService" not in source
    assert "get_streamlit_session" in source
    assert "Generate Interview Strategy" in source
