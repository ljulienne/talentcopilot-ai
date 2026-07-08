def test_command_center_imports():
    module = __import__("talentcopilot.ui.command_center", fromlist=["render_command_center"])
    assert hasattr(module, "render_command_center")


def test_logo_asset_exists():
    from pathlib import Path

    assert Path("assets/branding/talentcopilot_logo.svg").exists()
