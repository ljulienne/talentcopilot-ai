def test_tds_components_import():
    module = __import__("talentcopilot.ui.design_system.components", fromlist=["enterprise_hero", "section_title", "metric_grid", "insight_card", "status_badge", "activity_item", "next_action_card", "empty_state"])
    for attr in ["enterprise_hero", "section_title", "metric_grid", "insight_card", "status_badge", "activity_item", "next_action_card", "empty_state"]:
        assert hasattr(module, attr)

def test_tds_theme_import():
    module = __import__("talentcopilot.ui.design_system.theme", fromlist=["apply_enterprise_theme"])
    assert hasattr(module, "apply_enterprise_theme")
