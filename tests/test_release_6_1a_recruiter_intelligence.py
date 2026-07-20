import json

from talentcopilot.recruiter_intelligence import RecruiterIntelligenceEngine
from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline


JOB = """Senior International HRIS Project Manager. 10+ years. Lead global Core HR
transformations, migrations and interfaces. SAP SuccessFactors, Power BI,
stakeholder management, team leadership, French and English required."""


def test_assessment_is_grounded_and_job_aware():
    assessment = RecruiterIntelligenceEngine().assess(
        candidate_name="Vincent Blakoe",
        candidate_text="""Vincent Blakoe. 13 years Senior HRIS Project Manager.
        Led international SuccessFactors and Workday implementations, Core HR
        migrations, interfaces and global teams for BNP and Siemens.""",
        job_text=JOB,
        mission_fit=88,
        mission_breakdown={"function": 100, "experience": 95, "business_scope": 90},
    )
    assert assessment.strategic_fit_score >= 75
    assert assessment.candidate_dna.primary_archetype in {"Integrator", "Leader", "Transformer"}
    assert "International scope" in assessment.decisive_strengths
    serialized = json.dumps(assessment.to_dict()).lower()
    assert "successfactors" in serialized
    assert "power bi" not in serialized  # absent from the CV, never invented as evidence


def test_strategic_role_mismatch_is_visible():
    assessment = RecruiterIntelligenceEngine().assess(
        candidate_name="Loretta Danielson",
        candidate_text="""Loretta Danielson. International HR Director. HR strategy,
        M&A, leadership, change management and Oracle HR administration.""",
        job_text=JOB,
        mission_fit=58,
    )
    assert assessment.strategic_fit_score < 70
    assert "Transformation complexity" in assessment.material_gaps


def test_pipeline_exposes_recruiter_intelligence_without_changing_public_score_contract():
    output = RealRankingPipeline().run(
        RealRankingInput(
            job_filename="job.txt",
            job_text=JOB,
            candidates=[CandidateTextInput(
                filename="vincent.txt",
                text="Vincent Blakoe. 13 years Senior HRIS Project Manager. Led international SuccessFactors implementations, Core HR migrations, interfaces and teams.",
            )],
        )
    )
    ranked = output.ranked_candidates[0]
    profile = ranked.matching_output.decision_output.profile
    payload = json.loads(profile.metadata["recruiter_intelligence"])
    assert profile.metadata["recruiter_intelligence_engine"] == "recruiter-intelligence-v1.0"
    assert payload["candidate_name"] == ranked.candidate_name
    assert ranked.fit_score == int(round(profile.fit_score))
    assert payload["strategic_fit_score"] != 0


def test_dna_distinguishes_operator_from_transformer():
    engine = RecruiterIntelligenceEngine()
    operator = engine.assess(candidate_name="A", candidate_text="HRIS support maintenance administration and operations", job_text=JOB, mission_fit=50)
    transformer = engine.assess(candidate_name="B", candidate_text="Led global transformation migration implementation and change management", job_text=JOB, mission_fit=50)
    assert operator.candidate_dna.primary_archetype == "Operator"
    assert transformer.candidate_dna.primary_archetype in {"Transformer", "Integrator", "Leader"}
