import json

from talentcopilot.career_intelligence import CareerFitEngine
from talentcopilot.evidence_profiles import CandidateEvidenceProfileBuilder, MissionEvidenceProfileBuilder
from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline

JOB = """Senior International HRIS Project Manager. Lead global Core HR transformations, migrations, interfaces and SAP SuccessFactors implementations. 10+ years required. French and English."""


def report(name, text):
    cp = CandidateEvidenceProfileBuilder().build(candidate_text=text, candidate_name=name)
    mp = MissionEvidenceProfileBuilder().build(job_text=JOB)
    return CareerFitEngine().assess(candidate_profile=cp, mission_profile=mp, candidate_text=text, job_text=JOB)


def test_recent_operational_hris_continuity_outscores_generalist_hr_direction():
    specialist = report("Zelma O'Reilly", """Zelma O'Reilly. Senior HRIS Manager. 11 years HRIS. Currently leads SAP SuccessFactors implementation, Core HR migrations, interfaces, deployment and support across Europe. French and English.""")
    generalist = report("Loretta Danielson", """Loretta Danielson. International HR Director. 15 years in HR. Current scope: HR strategy, talent management, employee relations, compensation and recruitment. Earlier experience included an HRIS project and SAP support. English and French.""")
    assert specialist.score > generalist.score
    assert specialist.recent_role_alignment > generalist.recent_role_alignment
    assert generalist.career_drift > specialist.career_drift


def test_engine_is_name_independent_and_deterministic():
    text = "Senior HRIS Manager. 12 years HRIS. Leads Workday and SuccessFactors rollouts, migration, interfaces and global teams."
    a = report("Candidate A", text)
    b = report("Candidate B", text)
    assert a.score == b.score
    assert a.to_dict()["dimensions"] == b.to_dict()["dimensions"]


def test_pipeline_preserves_mission_fit_and_exposes_dual_ranking_contract():
    candidates = [
        CandidateTextInput(filename="specialist.txt", text="Zelma O'Reilly. Senior HRIS Manager. 11 years HRIS. Currently leads SuccessFactors implementation, migration, interfaces and global support."),
        CandidateTextInput(filename="generalist.txt", text="Loretta Danielson. International HR Director. 15 years HR. Current scope HR strategy, talent management, employee relations and recruitment. Earlier HRIS project exposure."),
    ]
    output = RealRankingPipeline().run(RealRankingInput("job.txt", JOB, candidates))
    for item in output.ranked_candidates:
        metadata = item.matching_output.decision_output.profile.metadata
        payload = json.loads(metadata["career_intelligence"])
        assert metadata["decision_ranking_contract"] == "decision-ranking-v1.0"
        assert item.fit_score == int(round(item.matching_output.decision_output.profile.fit_score))
        assert item.decision_score == float(metadata["decision_score"])
        assert payload["candidate_name"] == item.candidate_name
        assert item.mission_fit_rank >= 1


def test_decision_priority_can_resolve_close_mission_fit_using_career_evidence():
    pipeline = RealRankingPipeline()
    stronger = pipeline._decision_score(mission_fit=60, career_fit=88, recruiter_fit=70, confidence=80)
    weaker = pipeline._decision_score(mission_fit=62, career_fit=42, recruiter_fit=66, confidence=80)
    assert stronger > weaker
