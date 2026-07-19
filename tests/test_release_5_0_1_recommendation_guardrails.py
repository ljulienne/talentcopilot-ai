from talentcopilot.mission_fit_v2 import MissionFitEngineV2
from talentcopilot.real_matching.models import RealMatchingInput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline


def test_mission_fit_rejects_critical_function_and_experience_mismatch():
    result = MissionFitEngineV2().evaluate(
        job_text=(
            "Transformation Lead Requirements Minimum 6 years experience. "
            "Project Management Stakeholder Management HRIS"
        ),
        candidate_text=(
            "David Smith Experience 1 years experience. Skills Graphic Design"
        ),
        candidate_name="David Smith",
    )

    assert result.recommendation == "Reject"
    assert result.risk_level == "Critical"


def test_real_matching_preserves_stable_reject_contract():
    output = RealMatchingPipeline().run(
        RealMatchingInput(
            candidate_filename="cv.txt",
            candidate_text=(
                "David Smith\nExperience\n1 years experience.\n"
                "Skills\nGraphic Design"
            ),
            job_filename="job.txt",
            job_text=(
                "Transformation Lead\nRequirements\nMinimum 6 years experience. "
                "Project Management Stakeholder Management HRIS"
            ),
            expected_salary=50000,
        )
    )

    assert output.decision_output.profile.recommendation == "Reject"
