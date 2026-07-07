from talentcopilot.ai.enterprise_pipeline import EnterprisePipeline
from talentcopilot.ai.product_readiness_engine import ProductReadinessEngine
from talentcopilot.ai.recruiter_workflow_engine import RecruiterWorkflowEngine
from talentcopilot.models.product_readiness import ReadinessLevel


def test_product_readiness_engine_with_session_and_workflow():
    session = EnterprisePipeline().run(
        {"title": "Transformation Lead", "required_skills": ["Project Management"]},
        [{"name": "Alice", "skills": ["Project Management"]}],
    )
    workflow = RecruiterWorkflowEngine().build_workflow(session)

    report = ProductReadinessEngine().assess(session, workflow)

    assert report.product_name
    assert report.version
    assert report.readiness_score >= 0
    assert report.readiness_level in set(ReadinessLevel)


def test_product_readiness_engine_without_session():
    report = ProductReadinessEngine().assess()

    assert report.failed_count >= 1
    assert report.readiness_score < 100
