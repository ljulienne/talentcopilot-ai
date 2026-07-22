from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERVIEW = (ROOT / "talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")
COMPARISON = (ROOT / "talentcopilot/ui/comparison_workspace.py").read_text(encoding="utf-8")
DECISION = (ROOT / "talentcopilot/ui/decision_board.py").read_text(encoding="utf-8")


def test_interview_saves_evidence_and_routes_to_comparison():
    assert "save_interview_evaluation(" in INTERVIEW
    assert 'request_page("Comparison"' in INTERVIEW
    assert "official matching score" in INTERVIEW


def test_comparison_preserves_official_score_and_requires_finalists():
    assert "Official Mission Fit" in COMPARISON
    assert "Select at least two finalists" in COMPARISON
    assert "mark_finalists_compared()" in COMPARISON
    assert 'request_page("Decision Board"' in COMPARISON


def test_decision_board_records_human_decision_with_rationale():
    assert "save_final_decision(" in DECISION
    assert "Decision rationale" in DECISION
    assert "Official Match" in DECISION
