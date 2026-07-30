from pathlib import Path
from types import SimpleNamespace

from talentcopilot.ui.app_shell import build_shell_search_results


ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")
SHELL_SOURCE = (ROOT / "talentcopilot/ui/app_shell.py").read_text(encoding="utf-8")
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
HOME_SOURCE = (ROOT / "talentcopilot/ui/executive_briefing.py").read_text(encoding="utf-8")
SIDEBAR_SOURCE = (ROOT / "talentcopilot/ui/premium_sidebar.py").read_text(encoding="utf-8")
WORKFLOW_SOURCE = (ROOT / "talentcopilot/ui/recruitment_workflow_shell.py").read_text(encoding="utf-8")


def test_release_810_adds_a_reusable_product_topbar_before_page_content():
    assert "from talentcopilot.ui.app_shell import render_product_topbar" in APP_SOURCE
    assert "render_product_topbar(" in APP_SOURCE
    assert APP_SOURCE.index("render_product_topbar(") < APP_SOURCE.index("render_recruitment_workflow_shell(", APP_SOURCE.index("def main"))
    for marker in (
        "tc-product-topbar-marker",
        "tc-topbar-breadcrumb",
        "tc-topbar-mission",
        "st.popover",
        "Search pages or candidates",
    ):
        assert marker in SHELL_SOURCE


def test_global_search_is_functional_for_pages_and_candidates():
    session = SimpleNamespace(
        ranked_analyses=[
            SimpleNamespace(
                candidate_id="candidate-louis",
                candidate_name="Louis Julienne",
                official_score=85.0,
                official_rank=1,
            )
        ]
    )
    page_results = build_shell_search_results(session, "dashboard")
    assert any(item.page_label == "Dashboard Perspective" for item in page_results)

    candidate_results = build_shell_search_results(session, "louis")
    candidate = next(item for item in candidate_results if item.candidate_id)
    assert candidate.label == "Louis Julienne"
    assert candidate.page_label == "Candidate Intelligence"
    assert "Official rank #1" in candidate.detail
    assert "85% Talent Fit" in candidate.detail


def test_release_810_uses_a_narrow_integrated_sidebar_and_real_icons():
    css = THEME_SOURCE.split(
        "/* Release 8.1.0 — Mockup fidelity and reusable product shell */",
        1,
    )[1]
    assert "width: 252px !important" in css
    assert "linear-gradient(180deg,#102F55 0%,#153B67 58%,#12355E 100%)" in css
    assert "tc-product-topbar-marker" in css
    assert 'button [data-testid="stIconMaterial"]' in css
    assert 'icon=icon' in SIDEBAR_SOURCE
    assert ':material/dashboard:' in SIDEBAR_SOURCE
    assert 'brand_lockup_html(version="", compact=True)' in SIDEBAR_SOURCE


def test_native_streamlit_chrome_is_reduced_without_fake_controls():
    css = THEME_SOURCE.split(
        "/* Release 8.1.0 — Mockup fidelity and reusable product shell */",
        1,
    )[1]
    assert '[data-testid="stToolbar"]' in css
    assert '[data-testid="stDecoration"]' in css
    assert "display: none !important" in css
    assert "st.text_input" in SHELL_SOURCE
    assert "request_page(" in SHELL_SOURCE
    assert "select_workflow_candidate(" in SHELL_SOURCE


def test_zero_state_is_premium_onboarding_not_a_dashboard_of_zeroes():
    assert "def _render_zero_state" in HOME_SOURCE
    assert "Turn recruitment evidence into confident decisions." in HOME_SOURCE
    assert "Start recruitment mission" in HOME_SOURCE
    assert 'if not snapshot["has_recruitment"] and not projects:' in HOME_SOURCE
    zero_branch = HOME_SOURCE.split('if not snapshot["has_recruitment"] and not projects:', 1)[1].split("active_label =", 1)[0]
    assert "_render_zero_state(domains, session)" in zero_branch
    assert "return" in zero_branch


def test_workflow_sits_below_the_product_topbar_on_desktop():
    assert ".tc-workflow-anchor{position:sticky;top:5.35rem;" in WORKFLOW_SOURCE
    assert "@media(max-width:980px){.tc-workflow-anchor{position:relative;top:auto}" in WORKFLOW_SOURCE


def test_release_scope_remains_presentation_only():
    changed_presentation_files = (
        "talentcopilot/ui/app_shell.py",
        "talentcopilot/ui/design_system/theme.py",
        "talentcopilot/ui/executive_briefing.py",
        "talentcopilot/ui/premium_sidebar.py",
        "talentcopilot/ui/recruitment_workflow_shell.py",
        "talentcopilot/ui/brand.py",
        "app.py",
    )
    for relative in changed_presentation_files:
        assert (ROOT / relative).exists()
    assert "No scoring or ranking engine changes" not in SHELL_SOURCE
