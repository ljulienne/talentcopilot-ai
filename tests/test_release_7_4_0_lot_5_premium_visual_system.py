from pathlib import Path

from talentcopilot.ui.design_system.foundations import (
    COLORS,
    RADIUS,
    SEMANTIC_STATES,
    SHADOWS,
    SPACING,
    TYPOGRAPHY,
)

ROOT = Path(__file__).resolve().parents[1]
THEME = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
COMPONENTS = (ROOT / "talentcopilot/ui/design_system/components.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / "talentcopilot/ui/recruitment_workflow_shell.py").read_text(encoding="utf-8")
CANDIDATE = (ROOT / "talentcopilot/ui/candidate_workspace.py").read_text(encoding="utf-8")
INTERVIEW = (ROOT / "talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")
COMPARISON = (ROOT / "talentcopilot/ui/comparison_workspace.py").read_text(encoding="utf-8")
DECISION = (ROOT / "talentcopilot/ui/decision_board.py").read_text(encoding="utf-8")


def test_premium_tokens_cover_visual_and_semantic_foundations():
    assert COLORS["surface"] == "#FFFFFF"
    assert "primary_strong" in COLORS
    assert "pill" in RADIUS
    assert "focus" in SHADOWS
    assert "2xl" in SPACING
    assert "display" in TYPOGRAPHY
    for state in ("complete", "current", "pending", "blocked", "strong", "partial", "missing"):
        assert state in SEMANTIC_STATES
        assert SEMANTIC_STATES[state]["symbol"]


def test_theme_styles_streamlit_primitives_and_responsive_layout():
    for contract in (
        'data-testid="stMetric"',
        'data-testid="stExpander"',
        'data-testid="stDataFrame"',
        '.stButton > button',
        '@media (max-width: 760px)',
        ':focus-visible',
    ):
        assert contract in THEME


def test_components_escape_content_and_supply_unique_empty_state_keys():
    assert "from html import escape" in COMPONENTS
    assert "tc_empty_state_" in COMPONENTS
    assert 'type="primary"' in COMPONENTS
    assert "use_container_width=True" in COMPONENTS


def test_workflow_is_compact_semantic_and_uses_hashed_widget_keys():
    assert "tc-workflow-bar" in WORKFLOW
    assert "Current stage:" in WORKFLOW
    assert "accessible_state" in WORKFLOW
    assert "hashlib.sha1" in WORKFLOW
    assert 'key=_key("previous"' in WORKFLOW
    assert 'key=_key("continue"' in WORKFLOW


def test_recruitment_decision_pages_keep_shared_theme_without_score_changes():
    for source in (CANDIDATE, INTERVIEW, COMPARISON, DECISION):
        assert "apply_enterprise_theme()" in source
    assert "Official Mission Fit" in COMPARISON
    assert "Official Match" in DECISION
    assert "match_score" in CANDIDATE


def test_lot_5_is_presentation_only():
    forbidden = (
        "match_score =",
        "rank =",
        "save_final_decision =",
        "save_interview_evaluation =",
    )
    combined = "\n".join((THEME, COMPONENTS, WORKFLOW))
    for fragment in forbidden:
        assert fragment not in combined
