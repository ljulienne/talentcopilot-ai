from talentcopilot.interview.models import InterviewCompetency
from talentcopilot.interview.plan_service import InterviewPlanService
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.readiness_service import InterviewReadinessService
from talentcopilot.interview.evaluation_service import InterviewEvaluationService


def test_interview_readiness_service():
    competencies = [
        InterviewCompetency("Leadership", "High", 92, False),
        InterviewCompetency("Communication", "Medium", 70, True),
    ]

    readiness = InterviewReadinessService().calculate(85, 82, competencies)

    assert readiness.score > 0
    assert readiness.status
    assert readiness.drivers


def test_interview_plan_service():
    plan = InterviewPlanService().build(["Leadership", "Communication"])

    assert plan.total_minutes > 0
    assert len(plan.sections) >= 4


def test_interview_question_service():
    competencies = [InterviewCompetency("Leadership", "Medium", 70, True)]
    questions = InterviewQuestionService().build(competencies)

    assert questions
    assert questions[0].expected_evidence
    assert questions[0].follow_ups


def test_interview_evaluation_service():
    competencies = [InterviewCompetency("Leadership", "High", 90, False)]
    scorecard = InterviewEvaluationService().build_scorecard(competencies)

    assert scorecard
    assert scorecard[0].suggested_score >= 1
