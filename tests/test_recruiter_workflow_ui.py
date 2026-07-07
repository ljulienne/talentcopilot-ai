from talentcopilot.models.recruiter_workflow import (
    RecruiterWorkflowReport,
    WorkflowStageStatus,
)
from talentcopilot.ui.recruiter_workflow_cards import render_recruiter_workflow


def test_recruiter_workflow_ui_import_safe():
    report = RecruiterWorkflowReport(
        role_title="Role",
        session_id="s1",
        overall_status=WorkflowStageStatus.IN_PROGRESS,
        recommended_next_action="Continue.",
    )

    render_recruiter_workflow(report)
