import json

from talentcopilot.evidence_profiles import CandidateEvidenceProfileBuilder, MissionEvidenceProfileBuilder
from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline

JOB = """Senior International HRIS Project Manager. 10+ years required. Lead global Core HR transformations, migrations and interfaces. SAP SuccessFactors is mandatory. Power BI preferred. French and English required."""
CV = """Vincent Blakoe. Senior HRIS Project Manager with 13 years of experience. Led international SAP SuccessFactors and Workday implementations, Core HR migrations, interfaces and global teams. French and English."""


def test_candidate_profile_is_normalized_traceable_and_deterministic():
    first = CandidateEvidenceProfileBuilder().build(candidate_text=CV, candidate_name="Vincent Blakoe")
    second = CandidateEvidenceProfileBuilder().build(candidate_text=CV, candidate_name="Vincent Blakoe")
    assert first.profile_version == "candidate-evidence-profile-v1.0"
    assert "SAP SuccessFactors" in first.technologies
    assert {"French", "English"}.issubset(set(first.languages))
    assert first.source_text_hash == second.source_text_hash
    assert [e.evidence_id for e in first.evidence] == [e.evidence_id for e in second.evidence]
    assert all(e.excerpt and e.source_kind == "candidate_cv" for e in first.evidence)


def test_mission_profile_identifies_role_seniority_and_critical_criteria():
    profile = MissionEvidenceProfileBuilder().build(job_text=JOB)
    assert profile.role_title == "Senior International HRIS Project Manager"
    assert profile.seniority == "senior"
    assert profile.minimum_years_experience == 10
    assert "SAP SuccessFactors" in profile.technologies
    assert "SAP SuccessFactors" in profile.critical_criteria
    assert all(e.source_kind == "job_description" for e in profile.evidence)


def test_pipeline_exposes_profiles_without_changing_official_score_or_rank_contract():
    output = RealRankingPipeline().run(RealRankingInput(job_filename="job.txt", job_text=JOB, candidates=[CandidateTextInput(filename="vincent.txt", text=CV)]))
    ranked = output.ranked_candidates[0]
    metadata = ranked.matching_output.decision_output.profile.metadata
    candidate = json.loads(metadata["candidate_evidence_profile"])
    mission = json.loads(metadata["mission_evidence_profile"])
    assert metadata["evidence_profile_contract"] == "evidence-profile-foundation-v1.0"
    assert candidate["candidate_name"] == ranked.candidate_name
    assert mission["role_title"]
    assert ranked.rank == 1
    assert ranked.fit_score == int(round(ranked.matching_output.decision_output.profile.fit_score))


def test_profiles_do_not_define_official_score_or_rank_fields():
    candidate = CandidateEvidenceProfileBuilder().build(candidate_text=CV, candidate_name="Vincent Blakoe").to_dict()
    mission = MissionEvidenceProfileBuilder().build(job_text=JOB).to_dict()
    forbidden = {"fit_score", "official_score", "ranking_score", "rank"}
    assert forbidden.isdisjoint(candidate)
    assert forbidden.isdisjoint(mission)
