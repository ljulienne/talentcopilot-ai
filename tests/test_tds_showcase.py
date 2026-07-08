def test_tds_showcase_import():
    module = __import__("talentcopilot.ui.design_system.showcase", fromlist=["render_design_system_showcase"])
    assert hasattr(module, "render_design_system_showcase")

def test_logo_asset_exists():
    from pathlib import Path
    assert Path("assets/branding/talentcopilot_logo.svg").exists()
