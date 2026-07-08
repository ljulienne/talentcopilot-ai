from talentcopilot.services.decision_core_demo_service import DecisionCoreDemoService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_decision_core_demo_service_runs():
    output = DecisionCoreDemoService().run("No fit candidate")

    assert output.profile.candidate_name == "David Smith"
    assert output.profile.recommendation == "Reject"
    assert output.engine_status["recommendation_intelligence"] == "OK"


def test_decision_core_navigation_still_exists():
    page = get_page_by_label("Decision Core")
    assert page is not None
