from talentcopilot.real_matching.models import RealMatchingInput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline
from talentcopilot.services.real_matching_demo_service import RealMatchingDemoService


def test_real_matching_pipeline_strong_candidate():
    output = RealMatchingPipeline().run(
        RealMatchingInput(
            candidate_filename="cv.txt",
            candidate_text=(
                "Alice Martin\nExperience\n8 years experience leading HRIS transformation.\n"
                "Skills\nHRIS Project Management Stakeholder Management Leadership"
            ),
            job_filename="job.txt",
            job_text=(
                "Transformation Lead\nRequirements\nMinimum 6 years experience. "
                "Project Management Stakeholder Management HRIS\nCompensation\n85000 100000"
            ),
            expected_salary=90000,
        )
    )

    assert output.extracted_candidate.candidate_name
    assert output.role_profile.role_title
    assert output.decision_output.profile.recommendation
    assert output.decision_output.profile.fit_score is not None


def test_real_matching_pipeline_rejects_no_fit():
    output = RealMatchingPipeline().run(
        RealMatchingInput(
            candidate_filename="cv.txt",
            candidate_text="David Smith\nExperience\n1 years experience.\nSkills\nGraphic Design",
            job_filename="job.txt",
            job_text="Transformation Lead\nRequirements\nMinimum 6 years experience. Project Management Stakeholder Management HRIS",
            expected_salary=50000,
        )
    )

    assert output.decision_output.profile.recommendation == "Reject"


def test_real_matching_demo_service():
    demo = RealMatchingDemoService().run_demo()

    assert demo.output.recommendation
    assert demo.output.role_profile.required_skills
