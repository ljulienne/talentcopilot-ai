from talentcopilot.ui.design_system.foundations import COLORS, RADIUS, SHADOWS, SPACING, TYPOGRAPHY

def test_tds_foundations_tokens_exist():
    assert COLORS["primary"] == "#2563EB"
    assert COLORS["ai"] == "#7C3AED"
    assert COLORS["background"] == "#F8FAFC"
    assert RADIUS["lg"]
    assert SHADOWS["md"]
    assert SPACING["md"]
    assert TYPOGRAPHY["font_family"]
