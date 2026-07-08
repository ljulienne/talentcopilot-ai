from talentcopilot.hybrid_matching.decision_board_engine import HybridDecisionBoardEngine
from talentcopilot.services.hybrid_decision_board_service import HybridDecisionBoardService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_hybrid_decision_board_demo(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")

    board = HybridDecisionBoardService().run_demo().board

    assert board.total_candidates == 3
    assert board.top_candidate is not None
    assert board.top_candidate.final_score >= 0


def test_hybrid_decision_board_ranking_order(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")

    board = HybridDecisionBoardService().run_demo().board
    scores = [candidate.final_score for candidate in board.candidates]

    assert scores == sorted(scores, reverse=True)


def test_hybrid_decision_board_navigation():
    page = get_page_by_label("Hybrid Decision Board")

    assert page is not None
    assert page.module == "talentcopilot.ui.hybrid_decision_board"


def test_hybrid_decision_board_ui_imports():
    module = __import__("talentcopilot.ui.hybrid_decision_board", fromlist=["render_hybrid_decision_board"])

    assert hasattr(module, "render_hybrid_decision_board")
