from talentcopilot.decision_core.workspace_bridge import DecisionCoreWorkspaceBridge
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_workspace_bridge_demo_creates_profiles():
    report = DecisionCoreWorkspaceBridge().build_demo()

    assert report.status == "Ready"
    assert report.profiles_created == 2
    assert report.outputs[0].profile.recommendation


def test_decision_core_bridge_navigation_still_exists():
    page = get_page_by_label("Decision Core Bridge")
    assert page is not None
