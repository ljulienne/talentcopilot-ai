from talentcopilot.models.command_center import (
    CommandCenterActivity,
    CommandCenterMetric,
    CommandCenterPriority,
    CommandCenterReport,
    RecruitmentHealth,
)


def test_command_center_models():
    health = RecruitmentHealth(91, 96, 88, 94, "Very Low", 100)
    report = CommandCenterReport(
        role_title="Transformation Lead",
        session_id="s1",
        metrics=[CommandCenterMetric("Candidates", "3", "Analyzed")],
        priorities=[CommandCenterPriority("Review Alice", "Review evidence")],
        activities=[CommandCenterActivity("09:41", "Loaded", "Demo")],
        health=health,
    )

    assert report.role_title == "Transformation Lead"
    assert report.health.overall_score == 91
    assert report.metrics[0].label == "Candidates"
