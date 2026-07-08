def test_command_center_page_imports():
    module = __import__("talentcopilot.ui.command_center", fromlist=["render_command_center"])
    assert hasattr(module, "render_command_center")


def test_command_center_service_empty_report():
    from talentcopilot.services.command_center_service import CommandCenterService

    report = CommandCenterService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.metrics
    assert report.priorities
    assert report.health.overall_score == 0
