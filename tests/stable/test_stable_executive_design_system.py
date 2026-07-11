from talentcopilot.ui.executive import (
    THEME,
    TimelineStep,
    apply_executive_theme,
    normalize_percent,
    render_health_card,
    render_timeline,
    tone_color,
)


def test_executive_theme_tokens_are_stable():
    assert THEME.primary == "#2563EB"
    assert THEME.ai == "#7C3AED"
    assert THEME.radius >= 16


def test_percent_normalization_supports_fraction_and_percent():
    assert normalize_percent(0.92) == 92
    assert normalize_percent(92) == 92
    assert normalize_percent(150) == 100
    assert normalize_percent(-10) == 0


def test_tones_have_safe_fallback():
    assert tone_color("danger") == THEME.danger
    assert tone_color("unknown") == THEME.primary


def test_executive_components_are_import_safe():
    assert callable(apply_executive_theme)
    assert callable(render_health_card)
    assert callable(render_timeline)
    assert TimelineStep("Question").status == "complete"
