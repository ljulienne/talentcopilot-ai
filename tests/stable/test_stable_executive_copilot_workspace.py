from talentcopilot.executive_copilot import ExecutiveCopilotEngine
from talentcopilot.executive_copilot.context import ExecutiveCopilotContextBuilder
from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_context_builder_combines_multiple_engines():
    employees = dataframe_to_employees(demo_dataframe())
    context = ExecutiveCopilotContextBuilder().build(employees)
    assert context.insights
    assert context.decision_queue.decisions
    assert "Skills" in context.source_counts
    assert "Workforce" in context.source_counts


def test_workspace_question_returns_executive_response():
    employees = dataframe_to_employees(demo_dataframe())
    context = ExecutiveCopilotContextBuilder().build(employees)
    response = ExecutiveCopilotEngine().answer(
        insights=list(context.insights),
        decision_queue=context.decision_queue,
        question_id="HR-OVERVIEW-001",
    )
    assert response.answer.summary
    assert response.suggested_questions
    assert response.executive_health_score >= 0


def test_navigation_exposes_executive_copilot_workspace():
    page = get_page_by_label("Executive Copilot")
    assert page is not None
    assert page.module == "talentcopilot.ui.executive_copilot_workspace"
    assert page.function == "render_executive_copilot_workspace"
