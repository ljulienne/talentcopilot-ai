def test_enterprise_components_import():
    module = __import__("talentcopilot.ui.enterprise_components", fromlist=[
        "hero",
        "metric_row",
        "capability_grid",
        "workflow_steps",
        "context_panel",
        "safe_render",
    ])

    for attr in [
        "hero",
        "metric_row",
        "capability_grid",
        "workflow_steps",
        "context_panel",
        "safe_render",
    ]:
        assert hasattr(module, attr)
