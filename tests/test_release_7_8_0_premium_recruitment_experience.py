from pathlib import Path

from talentcopilot.ui.brand import APP_ICON_PATH, BRAND_NAME, BRAND_SLOGAN
from talentcopilot.ui.premium_sidebar import (
    RECRUITMENT_MENU_KEYS,
    RECRUITMENT_MENU_LABELS,
    active_menu_key,
    resolve_recruitment_destinations,
)

ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
CANDIDATE_SOURCE = (ROOT / "talentcopilot/ui/candidate_workspace.py").read_text(encoding="utf-8")
INTERVIEW_SOURCE = (ROOT / "talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")
WORKFLOW_SOURCE = (ROOT / "talentcopilot/ui/recruitment_workflow_shell.py").read_text(encoding="utf-8")


def test_brand_identity_is_centralized_and_replaceable():
    assert BRAND_NAME == "TalentCopilot-AI"
    assert BRAND_SLOGAN == "Human Intelligence. AI Amplified."
    assert APP_ICON_PATH.exists()


def test_sidebar_has_exactly_four_recruitment_destinations():
    assert RECRUITMENT_MENU_KEYS == ("overview", "candidates", "interview", "decide")
    assert RECRUITMENT_MENU_LABELS == ("Overview", "Candidates", "Interview", "Compare & decide")
    items = resolve_recruitment_destinations(None, current_page="Executive Brief")
    assert tuple(item.label for item in items) == RECRUITMENT_MENU_LABELS


def test_sidebar_no_longer_uses_radio_navigation():
    assert "st.sidebar.radio" not in APP_SOURCE
    assert "render_premium_sidebar" in APP_SOURCE
    assert 'div[role="radiogroup"]' in THEME_SOURCE


def test_sidebar_maps_hidden_workflow_routes_to_one_modern_entry():
    assert active_menu_key("Recruitment Overview") == "overview"
    assert active_menu_key("Recruitment Workspace") == "overview"
    assert active_menu_key("Candidate Intelligence") == "candidates"
    assert active_menu_key("Interview Intelligence") == "interview"
    assert active_menu_key("Comparison") == "decide"
    assert active_menu_key("Decision Board") == "decide"


def test_normal_primary_actions_are_not_red():
    assert "#1D4ED8" in THEME_SOURCE
    assert "#06B6D4" in THEME_SOURCE
    rule = THEME_SOURCE.rsplit('.stButton > button[kind="primary"]', 1)[1].split("}}", 1)[0]
    assert "#B91C1C" not in rule
    assert "red" not in rule.lower()


def test_candidate_workspace_has_three_non_nested_primary_sections():
    assert 'tab_overview, tab_competencies, tab_evidence = st.tabs([' in CANDIDATE_SOURCE
    assert '"Overview",\n        "Competencies",\n        "Evidence",' in CANDIDATE_SOURCE
    assert 'evidence_tab, risks_tab, interview_tab = st.tabs' not in CANDIDATE_SOURCE


def test_interview_workspace_has_three_guided_stages():
    assert 'tab_prepare, tab_conduct, tab_assessment = st.tabs([' in INTERVIEW_SOURCE
    assert '"Prepare",\n        "Conduct",\n        "Assessment",' in INTERVIEW_SOURCE
    assert 'tab_overview, tab_strategy, tab_live, tab_scorecard' not in INTERVIEW_SOURCE
    assert "Live Evaluation" in INTERVIEW_SOURCE


def test_workflow_strip_does_not_render_selection_circles():
    render_section = WORKFLOW_SOURCE.split("def render_recruitment_workflow_shell", 1)[1]
    assert 'aria-hidden="true">{symbol}' not in render_section
    assert "tc-workflow-state" in render_section
