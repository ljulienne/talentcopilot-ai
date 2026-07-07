from talentcopilot.ai.enterprise_pipeline import EnterprisePipeline
from talentcopilot.ai.recruiter_workflow_engine import RecruiterWorkflowEngine
from talentcopilot.models.recruiter_workflow import WorkflowStageStatus


def test_recruiter_workflow_from_completed_session():
    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management"],
    }
    candidates = [
        {"name": "Alice", "skills": ["Project Management"]},
        {"name": "Bob", "skills": ["Excel"]},
    ]

    session = EnterprisePipeline().run(job, candidates)
    report = RecruiterWorkflowEngine().build_workflow(session)

    assert report.role_title == "Transformation Lead"
    assert report.overall_status in {
        WorkflowStageStatus.IN_PROGRESS,
        WorkflowStageStatus.COMPLETED,
        WorkflowStageStatus.BLOCKED,
    }
    assert "Alice" in report.shortlist_candidate_names
    assert report.recommended_next_action


def test_recruiter_workflow_blocks_incomplete_intake():
    session = EnterprisePipeline().create_session(
        job={"title": ""},
        candidates=[],
    )

    report = RecruiterWorkflowEngine().build_workflow(session)

    assert report.overall_status == WorkflowStageStatus.BLOCKED
    assert report.blocked_count >= 1
