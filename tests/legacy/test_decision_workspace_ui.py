from talentcopilot.ui.decision_workspace import render_decision_workspace
from talentcopilot.ui.components.decision.header import render_decision_header
from talentcopilot.ui.components.decision.timeline import render_decision_timeline
from talentcopilot.ui.components.decision.summary import render_executive_summary
from talentcopilot.ui.components.decision.metrics import render_decision_metrics
from talentcopilot.ui.components.decision.recommendation import render_recommendation_panel
from talentcopilot.ui.components.decision.interview import render_interview_panel
from talentcopilot.ui.components.decision.actions import render_decision_actions


def test_decision_workspace_page_is_callable():
    assert callable(render_decision_workspace)


def test_decision_components_are_callable():
    assert callable(render_decision_header)
    assert callable(render_decision_timeline)
    assert callable(render_executive_summary)
    assert callable(render_decision_metrics)
    assert callable(render_recommendation_panel)
    assert callable(render_interview_panel)
    assert callable(render_decision_actions)
