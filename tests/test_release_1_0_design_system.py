def test_design_system_imports():
    imports = [
        ("talentcopilot.ui.design_system.foundations", "COLORS"),
        ("talentcopilot.ui.design_system.icons", "ICONS"),
        ("talentcopilot.ui.design_system.theme", "apply_enterprise_theme"),
        ("talentcopilot.ui.design_system.components", "enterprise_hero"),
        ("talentcopilot.ui.design_system.navigation", "get_enterprise_navigation"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)


def test_design_system_brand_colors():
    from talentcopilot.ui.design_system.foundations import COLORS

    assert COLORS["primary"] == "#2563EB"
    assert COLORS["ai"] == "#7C3AED"
    assert COLORS["background"] == "#F8FAFC"
