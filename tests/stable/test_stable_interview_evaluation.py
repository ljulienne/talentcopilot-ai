from talentcopilot.interview.evaluation_models import InterviewRating
from talentcopilot.interview.post_interview_evaluation_service import PostInterviewEvaluationService


def test_post_interview_evaluation_positive():
    ratings = [
        InterviewRating("Leadership", 5, True, "Strong answer"),
        InterviewRating("Communication", 4, True, "Clear examples"),
    ]

    summary = PostInterviewEvaluationService().evaluate("Alice Martin", ratings)

    assert summary.overall_score >= 4
    assert summary.decision_impact in {"Positive", "Strong positive"}
    assert summary.strengths_confirmed
    assert summary.recommendation_after_interview


def test_post_interview_evaluation_negative():
    ratings = [
        InterviewRating("Leadership", 2, False, "Vague"),
        InterviewRating("Communication", 2, False, "Weak"),
    ]

    summary = PostInterviewEvaluationService().evaluate("David Smith", ratings)

    assert summary.overall_score <= 2
    assert summary.decision_impact == "Negative"
    assert summary.risks_remaining


def test_post_interview_markdown_export():
    service = PostInterviewEvaluationService()
    summary = service.evaluate("Alice Martin", [InterviewRating("Leadership", 5, True, "Strong")])
    markdown = service.to_markdown(summary)

    assert "# Interview Evaluation" in markdown
    assert "Alice Martin" in markdown
    assert "Leadership" in markdown


def test_interview_workspace_import_after_evaluation_patch():
    module = __import__("talentcopilot.ui.interview_workspace", fromlist=["render_interview_workspace"])
    assert hasattr(module, "render_interview_workspace")
