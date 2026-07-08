def test_enterprise_shell_imports():
    module = __import__(
        "talentcopilot.ui.enterprise_shell",
        fromlist=["render_enterprise_brand", "render_workspace_caption", "render_current_recruitment"],
    )
    assert hasattr(module, "render_enterprise_brand")
    assert hasattr(module, "render_workspace_caption")
    assert hasattr(module, "render_current_recruitment")


def test_ui_showcase_imports():
    module = __import__("talentcopilot.ui.ui_showcase", fromlist=["render_ui_showcase"])
    assert hasattr(module, "render_ui_showcase")
