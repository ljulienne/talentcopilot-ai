from talentcopilot.decision_core.workspace_bridge import DecisionCoreWorkspaceBridge
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_workspace_bridge_no_session():
    report = DecisionCoreWorkspaceBridge().build_from_session(None)

    assert report.status == "No session"
    assert report.profiles_created == 0


def test_workspace_bridge_demo_creates_profiles():
    report = DecisionCoreWorkspaceBridge().build_demo()

    assert report.status == "Ready"
    assert report.profiles_created == 2
    assert report.outputs[0].profile.recommendation


def test_decision_core_bridge_imports():
    module = __import__("talentcopilot.ui.decision_core_bridge", fromlist=["render_decision_core_bridge"])
    assert hasattr(module, "render_decision_core_bridge")


def test_decision_core_bridge_navigation():
    page = get_page_by_label("Decision Core Bridge")
    assert page is not None
    assert page.module == "talentcopilot.ui.decision_core_bridge"
    assert page.function == "render_decision_core_bridge"
