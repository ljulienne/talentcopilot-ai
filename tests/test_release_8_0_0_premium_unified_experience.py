from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
HOME_SOURCE = (ROOT / "talentcopilot/ui/executive_briefing.py").read_text(encoding="utf-8")
SIDEBAR_SOURCE = (ROOT / "talentcopilot/ui/premium_sidebar.py").read_text(encoding="utf-8")
RELEASE_NOTES = (ROOT / "docs/RELEASE_NOTES_8_0_0.md").read_text(encoding="utf-8")


def _release_800_css() -> str:
    return THEME_SOURCE.split(
        "/* Release 8.0.0 — Premium unified balanced experience */",
        1,
    )[1]


def test_release_800_uses_balanced_shell_not_all_dark_or_all_light():
    css = _release_800_css()
    assert "linear-gradient(180deg,#102A56 0%,#153764 58%,#102B53 100%)" in css
    assert "linear-gradient(180deg,#F5F7FC 0%,#EFF3FA 100%)" in css
    assert "background:#FCFDFE !important" in css
    assert "border-right: 1px solid #284B78 !important" in css


def test_sidebar_navigation_has_accessible_contrast_and_integrated_rows():
    css = _release_800_css()
    assert "color:#E7F0FC !important" in css
    assert "background:transparent !important" in css
    assert "box-shadow:none !important" in css
    assert "background:linear-gradient(105deg,#2949B8" in css
    assert "inset 3px 0 0 #63D4E7" in css


def test_sidebar_does_not_append_counts_to_navigation_labels():
    nav_function = SIDEBAR_SOURCE.split("def _nav_button", 1)[1].split("def render_premium_sidebar", 1)[0]
    assert "label +=" not in nav_function
    assert 'label = f"{item.glyph}  {item.label}"' in nav_function
    assert "Next up" in SIDEBAR_SOURCE


def test_home_is_a_real_data_backed_dashboard():
    for marker in (
        "tc-home-stat",
        "tc-home-panel",
        "Active recruitment",
        "Today’s priorities",
        "Active projects",
        "project.candidate_count",
        "project.analyzed_count",
        "project.progress_percent",
    ):
        assert marker in HOME_SOURCE
    for fabricated_mockup_value in ("126", "24 days", "87%", "15 shortlisted"):
        assert fabricated_mockup_value not in HOME_SOURCE


def test_home_preserves_diagnostics_and_mission_routing():
    assert "build_briefing_domains(session)" in HOME_SOURCE
    assert "_render_domain(domain" in HOME_SOURCE
    assert 'with st.expander("Describe a new mission"' in HOME_SOURCE
    assert "understand_mission(prompt)" in HOME_SOURCE


def test_release_preserves_business_outputs():
    assert "Official Talent Fit scores and ranks" in RELEASE_NOTES
    assert "PDF exports" in RELEASE_NOTES
    assert "No invented trend" in RELEASE_NOTES
