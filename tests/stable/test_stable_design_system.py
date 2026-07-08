from talentcopilot.ui.design_system.foundations import COLORS
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def test_design_system_tokens():
    assert COLORS["primary"] == "#2563EB"
    assert COLORS["ai"] == "#7C3AED"
    assert COLORS["background"] == "#F8FAFC"


def test_design_system_theme_callable():
    assert callable(apply_enterprise_theme)
