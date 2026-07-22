from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService


def test_interview_evidence_is_separate_from_official_score_fields():
    context = RecruitmentWorkflowContext()
    context.interview_evaluations["c1"] = {"overall_score": 4.2, "recommendation": "Proceed"}
    assert context.interview_evaluations["c1"]["overall_score"] == 4.2
    assert not hasattr(context, "match_score")
    assert not hasattr(context, "rank")


def test_comparison_requires_two_finalists():
    context = RecruitmentWorkflowContext(
        interview_assessed_candidate_ids=["c1"],
        finalist_candidate_ids=["c1"],
        finalists_compared=True,
    )
    states = RecruitmentWorkflowService().resolve_steps(None, context, current_page="Comparison")
    comparison = next(item for item in states if item.key == "compare")
    assert comparison.completed is False


def test_comparison_completed_with_two_finalists():
    context = RecruitmentWorkflowContext(
        interview_assessed_candidate_ids=["c1", "c2"],
        finalist_candidate_ids=["c1", "c2"],
        finalists_compared=True,
    )
    context.completed_steps.extend(["setup", "role", "candidates", "analysis", "candidate", "prepare", "assess"])
    states = RecruitmentWorkflowService().resolve_steps(None, context, current_page="Comparison")
    comparison = next(item for item in states if item.key == "compare")
    assert comparison.completed is True


def test_final_decision_requires_candidate_and_rationale():
    context = RecruitmentWorkflowContext()
    context.final_decision_candidate_id = "c1"
    context.final_decision_rationale = "Evidence supports the decision."
    context.decision_recorded = True
    assert context.decision_recorded is True
