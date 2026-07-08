from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput


def test_orchestrator_runs_full_pipeline_with_budget():
    output = DecisionCoreOrchestrator().analyze_candidate(
        DecisionCoreInput(
            candidate={
                "name": "Alice Martin",
                "skills": ["Project Management", "Stakeholder Management", "HRIS"],
                "years_experience": 8,
                "achievements": ["Improved adoption by 35%"],
            },
            role_title="Transformation Lead",
            required_skills=["Project Management", "Stakeholder Management"],
            preferred_skills=["HRIS"],
            minimum_years_experience=6,
            target_salary=85000,
            maximum_salary=100000,
            expected_salary=90000,
        )
    )

    assert output.profile.candidate_name == "Alice Martin"
    assert output.profile.recommendation
    assert output.engine_status["budget_intelligence"] == "OK"
    assert output.engine_status["recommendation_intelligence"] == "OK"
    assert output.pipeline_version == "dic-v2.0-alpha-i"


def test_orchestrator_rejects_no_fit_candidate():
    output = DecisionCoreOrchestrator().analyze_candidate(
        DecisionCoreInput(
            candidate={"name": "David Smith", "skills": ["Graphic Design"], "years_experience": 1},
            role_title="Transformation Lead",
            required_skills=["Project Management", "Stakeholder Management"],
            minimum_years_experience=6,
            target_salary=85000,
            maximum_salary=100000,
            expected_salary=50000,
        )
    )

    assert output.profile.fit_score < 30
    assert output.recommendation == "Reject"


def test_orchestrator_analyze_many():
    inputs = [
        DecisionCoreInput(candidate={"name": "Alice Martin", "skills": ["HRIS"]}, role_title="HRIS Lead", required_skills=["HRIS"]),
        DecisionCoreInput(candidate={"name": "David Smith", "skills": []}, role_title="HRIS Lead", required_skills=["HRIS"]),
    ]

    outputs = DecisionCoreOrchestrator().analyze_many(inputs)

    assert len(outputs) == 2
    assert outputs[0].profile.profile_id != outputs[1].profile.profile_id
