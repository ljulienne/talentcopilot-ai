from talentcopilot.recruitment_reasoning import RecruitmentReasoningEngine
from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline


def test_reasoning_engine_builds_atomic_generic_criteria():
    result = RecruitmentReasoningEngine().evaluate(
        job_text=(
            "Senior systems project manager. Lead implementations, interfaces, "
            "acceptance testing, vendor management and Power BI reporting. "
            "At least 8 years experience. Fluent English required."
        ),
        candidate_text=(
            "10 years as systems project manager. Led implementations and APIs, "
            "managed vendors, UAT and built Power BI dashboards. English fluent."
        ),
        candidate_name="Alex Morgan",
    )
    keys = {item.key for item in result.criteria}
    assert "skill_project_management" in keys
    assert "integration" in keys
    assert "testing" in keys
    assert "vendor_management" in keys
    assert "tool_power_bi" in keys
    assert result.score >= 70
    assert result.assessments


def test_transferable_tools_receive_partial_not_full_credit():
    result = RecruitmentReasoningEngine().evaluate(
        job_text="Workday implementation lead required",
        candidate_text="Oracle HCM implementation lead",
    )
    tool = next(item for item in result.assessments if item.criterion.key == "tool_workday")
    assert tool.evidence_level == "transferable"
    assert 0 < tool.evidence_score < 1


def test_ranking_resolves_candidate_identity_before_output():
    job = "HRIS project manager with SuccessFactors, project management and English."
    candidate = """
    ABOUT ME
    Projects for AstraZeneca and Credit Suisse.
    Vincent BLAKOE
    vincent.blakoe@example.com
    13 years HRIS project management. SuccessFactors. English.
    """
    output = RealRankingPipeline().run(
        RealRankingInput(
            job_filename="job.txt",
            job_text=job,
            candidates=[CandidateTextInput(filename="Blakoe Vincent.pdf", text=candidate)],
        )
    )
    assert output.ranked_candidates[0].candidate_name == "Vincent Blakoe"
    trace = output.ranked_candidates[0].matching_output.decision_output.profile.metadata
    assert trace["recruitment_reasoning_engine"] == "recruitment-reasoning-v1.0"
    assert "recruitment_reasoning_trace" in trace
