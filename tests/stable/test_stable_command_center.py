from talentcopilot.services.command_center_service import CommandCenterService


def test_command_center_empty_report():
    report = CommandCenterService().build(None)
    assert report.role_title == "No active recruitment"
    assert report.metrics
    assert report.priorities
    assert report.health.overall_score == 0
