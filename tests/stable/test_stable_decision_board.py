from talentcopilot.services.decision_board_service import DecisionBoardService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_decision_board_empty_report():
    report = DecisionBoardService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.candidates == []
    assert report.next_actions


def test_decision_board_imports():
    module = __import__("talentcopilot.ui.decision_board", fromlist=["render_decision_board"])
    assert hasattr(module, "render_decision_board")


def test_decision_board_navigation():
    page = get_page_by_label("Decision Board")
    assert page is not None
    assert page.module == "talentcopilot.ui.decision_board"
    assert page.function == "render_decision_board"
