from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline
from talentcopilot.services.real_ranking_demo_service import RealRankingDemoService


def test_real_ranking_pipeline_orders_candidates():
    output = RealRankingPipeline().run(
        RealRankingInput(
            job_filename="job.txt",
            job_text="Transformation Lead\nRequirements\nMinimum 6 years experience. Project Management Stakeholder Management HRIS",
            candidates=[
                CandidateTextInput("alice.txt", "Alice Martin\n8 years experience\nSkills\nHRIS Project Management Stakeholder Management"),
                CandidateTextInput("david.txt", "David Smith\n1 years experience\nSkills\nGraphic Design"),
            ],
        )
    )

    assert output.total_candidates == 2
    assert output.ranked_candidates[0].rank == 1
    assert output.ranked_candidates[0].ranking_score >= output.ranked_candidates[1].ranking_score
    assert output.ranked_candidates[-1].recommendation == "Reject"


def test_real_ranking_demo_service():
    demo = RealRankingDemoService().run_demo()

    assert demo.output.ranked_candidates
    assert demo.output.ranked_candidates[0].rank == 1


def test_ranking_score_bounds():
    output = RealRankingDemoService().run_demo().output
    for item in output.ranked_candidates:
        assert 0 <= item.ranking_score <= 100
