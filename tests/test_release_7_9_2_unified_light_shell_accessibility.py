from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
RELEASE_NOTES = (ROOT / "docs/RELEASE_NOTES_7_9_2.md").read_text(encoding="utf-8")


def _relative_luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    channels = [int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)]

    def linear(channel: float) -> float:
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_release_adds_a_light_unified_application_shell():
    assert "Release 7.9.2 — Unified light shell and accessible navigation" in THEME_SOURCE
    assert "linear-gradient(180deg,#F8FBFF 0%,#F3F7FC 100%) !important" in THEME_SOURCE
    assert "border-right: 1px solid #DCE6F3 !important" in THEME_SOURCE
    assert '[data-testid="stAppViewContainer"]' in THEME_SOURCE
    assert '[data-testid="stHeader"]' in THEME_SOURCE


def test_inactive_navigation_is_an_integrated_high_contrast_row():
    assert "color: #334155 !important" in THEME_SOURCE
    assert "background: transparent !important" in THEME_SOURCE
    assert "border: 1px solid transparent !important" in THEME_SOURCE
    assert "box-shadow: none !important" in THEME_SOURCE
    assert _contrast_ratio("#334155", "#F8FAFC") >= 4.5


def test_active_navigation_is_light_blue_and_accessible():
    assert "color: #0F4CD8 !important" in THEME_SOURCE
    assert "background: #E8F0FF !important" in THEME_SOURCE
    assert "inset 3px 0 0 #2563EB" in THEME_SOURCE
    assert _contrast_ratio("#0F4CD8", "#E8F0FF") >= 4.5


def test_nested_streamlit_button_text_inherits_the_accessible_color():
    assert 'button[data-testid^="stBaseButton"] p' in THEME_SOURCE
    assert 'button[data-testid^="stBaseButton"] span' in THEME_SOURCE
    assert "color: inherit !important" in THEME_SOURCE
    assert "opacity: 1 !important" in THEME_SOURCE


def test_sidebar_context_and_supporting_states_are_lightened():
    for selector in (
        ".tc-brand-name",
        ".tc-brand-slogan",
        ".tc-mission-card",
        ".tc-sidebar-next",
        ".tc-nav-notice",
    ):
        assert selector in THEME_SOURCE
    assert "background:#FFFFFF !important" in THEME_SOURCE
    assert "background:#ECFEFF !important" in THEME_SOURCE


def test_release_preserves_business_engines_and_prior_rendering_hotfix():
    assert "Official Talent Fit scores and ranks" in RELEASE_NOTES
    assert "PDF exports" in RELEASE_NOTES
    assert "Release 7.9.1 HTML-rendering fixes" in RELEASE_NOTES
