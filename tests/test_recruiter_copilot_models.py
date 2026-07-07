from talentcopilot.models.recruiter_copilot import (
    CopilotAction,
    CopilotActionType,
    CopilotAlert,
    CopilotPriority,
    RecruiterCopilotReport,
)


def test_recruiter_copilot_report_properties():
    report = RecruiterCopilotReport(
        candidate_name="Alice",
        role_title="Transformation Lead",
        headline="Hire",
        recruiter_summary="Summary",
        actions=[
            CopilotAction(
                action_type=CopilotActionType.MOVE_FORWARD,
                priority=CopilotPriority.HIGH,
                title="Move forward",
                rationale="Strong fit",
            )
        ],
        alerts=[
            CopilotAlert(
                severity=CopilotPriority.HIGH,
                title="Validate",
                message="Needs validation",
            )
        ],
    )

    assert report.action_count == 1
    assert report.has_high_priority_alerts is True
