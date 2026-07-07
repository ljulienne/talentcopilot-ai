from talentcopilot.models.recruiter_workflow import (
    RecruiterWorkflowReport,
    WorkflowStage,
    WorkflowStageName,
    WorkflowStageStatus,
)


def test_recruiter_workflow_report_counts():
    report = RecruiterWorkflowReport(
        role_title="Role",
        session_id="s1",
        overall_status=WorkflowStageStatus.IN_PROGRESS,
        stages=[
            WorkflowStage(
                name=WorkflowStageName.INTAKE,
                status=WorkflowStageStatus.COMPLETED,
                explanation="Done",
            ),
            WorkflowStage(
                name=WorkflowStageName.CANDIDATE_ANALYSIS,
                status=WorkflowStageStatus.BLOCKED,
                explanation="Blocked",
            ),
        ],
    )

    assert report.completed_count == 1
    assert report.blocked_count == 1
