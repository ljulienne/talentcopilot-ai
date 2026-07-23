from talentcopilot.ui.design_system.foundations import COLORS
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def test_design_system_tokens():
    assert COLORS["primary"] == "#4F46E5"
    assert COLORS["ai"] == "#7C3AED"
    assert COLORS["background"] == '#F6F7FB'


def test_design_system_theme_callable():
    assert callable(apply_enterprise_theme)
