from pathlib import Path

from talentcopilot.ui.design_system.components import (
    compact_empty_state,
    loading_skeleton,
    page_header,
    recommended_action,
)


ROOT = Path(__file__).resolve().parents[1]
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
COMPONENT_SOURCE = (ROOT / "talentcopilot/ui/design_system/components.py").read_text(encoding="utf-8")
WORKFLOW_SOURCE = (ROOT / "talentcopilot/ui/recruitment_workflow_shell.py").read_text(encoding="utf-8")
DASHBOARD_SOURCE = (ROOT / "talentcopilot/ui/recruitment_overview.py").read_text(encoding="utf-8")
CANDIDATE_SOURCE = (ROOT / "talentcopilot/ui/candidate_workspace.py").read_text(encoding="utf-8")
INTERVIEW_SOURCE = (ROOT / "talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")
COMPENSATION_SOURCE = (ROOT / "talentcopilot/ui/hiring_budget.py").read_text(encoding="utf-8")
COMPARISON_SOURCE = (ROOT / "talentcopilot/ui/comparison_workspace.py").read_text(encoding="utf-8")
WORKSPACE_SOURCE = (ROOT / "talentcopilot/ui/design_system/v2/workspace.py").read_text(encoding="utf-8")


def test_release_790_exposes_reusable_premium_components():
    assert callable(page_header)
    assert callable(recommended_action)
    assert callable(compact_empty_state)
    assert callable(loading_skeleton)
    assert "tc-page-header" in COMPONENT_SOURCE
    assert "tc-recommended-action" in COMPONENT_SOURCE
    assert "tc-empty-state" in COMPONENT_SOURCE
    assert "tc-skeleton" in COMPONENT_SOURCE


def test_recruitment_pages_use_one_compact_header_pattern():
    for source in (
        DASHBOARD_SOURCE,
        CANDIDATE_SOURCE,
        INTERVIEW_SOURCE,
        COMPENSATION_SOURCE,
        COMPARISON_SOURCE,
    ):
        assert "page_header(" in source
    assert "Recruitment · Candidate portfolio" in DASHBOARD_SOURCE
    assert "Recruitment · Candidate detail" in CANDIDATE_SOURCE
    assert "Recruitment · Structured interview" in INTERVIEW_SOURCE
    assert "Recruitment · Financial alignment" in COMPENSATION_SOURCE
    assert "Recruitment · Final comparison" in COMPARISON_SOURCE


def test_workflow_shell_is_compact_sticky_and_decision_oriented():
    assert "position:sticky" in WORKFLOW_SOURCE
    assert "tc-workflow-top" in WORKFLOW_SOURCE
    assert "height:31px" in WORKFLOW_SOURCE
    assert "linear-gradient(90deg,#1D4ED8" in WORKFLOW_SOURCE
    assert "Next recommended action" in WORKFLOW_SOURCE
    assert "min-height:50px" not in WORKFLOW_SOURCE


def test_sidebar_contrast_and_density_are_strengthened():
    assert "width:286px !important" in THEME_SOURCE
    assert "color:#F4F8FF" in THEME_SOURCE
    assert "color:#D6E3F4" in THEME_SOURCE
    assert "font-weight:780" in THEME_SOURCE
    assert "min-height:2.48rem" in THEME_SOURCE


def test_dashboard_defaults_to_compact_list_and_preserves_card_mode():
    assert 'display_mode = st.segmented_control(' in DASHBOARD_SOURCE
    assert '"Display"' in DASHBOARD_SOURCE
    assert '["List", "Cards"]' in DASHBOARD_SOURCE
    assert 'default="List"' in DASHBOARD_SOURCE
    assert "tc-candidate-row" in DASHBOARD_SOURCE
    assert "dashboard_open_candidate_list_" in DASHBOARD_SOURCE
    assert "dashboard_open_candidate_" in DASHBOARD_SOURCE
    assert "candidate.strongest_area" in DASHBOARD_SOURCE
    assert "candidate.primary_risk" in DASHBOARD_SOURCE


def test_dashboard_uses_progressive_disclosure_for_advanced_analytics():
    assert 'with st.expander("Advanced portfolio analytics", expanded=False)' in DASHBOARD_SOURCE
    assert 'with st.expander("Quick candidate access", expanded=False)' in DASHBOARD_SOURCE
    assert "st.radio(" not in DASHBOARD_SOURCE
    assert 'st.segmented_control(\n        "Dashboard perspective"' in DASHBOARD_SOURCE


def test_dashboard_has_one_primary_recommended_action_at_top_level():
    assert "recommended_action(" in DASHBOARD_SOURCE
    assert 'key="recruitment_overview_next_action"' in DASHBOARD_SOURCE
    compare_block = DASHBOARD_SOURCE.split('key="dashboard_compare_finalists"', 1)[0].rsplit("st.button", 1)[1]
    assert 'type="primary"' not in compare_block


def test_existing_guided_sections_and_business_outputs_are_preserved():
    assert 'tab_overview, tab_competencies, tab_evidence = st.tabs([' in CANDIDATE_SOURCE
    assert 'tab_prepare, tab_conduct, tab_assessment = st.tabs([' in INTERVIEW_SOURCE
    assert "Download candidate report (PDF)" in CANDIDATE_SOURCE
    assert "Download interview report (PDF)" in INTERVIEW_SOURCE
    assert "Download compensation report (PDF)" in COMPENSATION_SOURCE
    assert "Download decision report (PDF)" in COMPARISON_SOURCE


def test_mission_workspace_header_is_compact_not_a_second_large_hero():
    assert ".tc-ew-hero{position:relative;padding:.95rem" in WORKSPACE_SOURCE
    assert ".tc-ew-title{font-size:1.55rem" in WORKSPACE_SOURCE
    assert "border-radius:16px" in WORKSPACE_SOURCE
