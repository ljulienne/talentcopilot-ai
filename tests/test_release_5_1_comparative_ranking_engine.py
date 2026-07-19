from pathlib import Path

from talentcopilot.comparative_ranking import ComparativeRankingEngine
from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline


JOB = """Senior Sales Manager APAC
12+ years B2B textile/apparel sales. 5+ years regional leadership.
Own an USD 80M+ business, manage country sales managers, multinational brands.
SAP Salesforce Power BI. English mandatory; Mandarin preferred.
"""


def _candidate(name: str, title: str, industry: str) -> CandidateTextInput:
    return CandidateTextInput(
        filename=f"{name}.txt",
        text=f"""{name}
Professional Summary
Experienced {title} with a background in {industry}.
Professional Experience 2012-2026
Led regional planning and commercial strategy across APAC.
Managed teams of 15-40 employees. Owned budgets, forecasts and strategic accounts.
Negotiated multi-million-dollar contracts. Business development and pricing.
SAP Salesforce Power BI. English fluent. MBA.
""",
    )


def test_comparative_engine_uses_role_scope_not_candidate_name():
    engine = ComparativeRankingEngine()
    director = engine.analyse("Person A", _candidate("Person A", "Regional Sales Director", "Textile").text, JOB)
    country = engine.analyse("Person B", _candidate("Person B", "Country Sales Manager", "Textile").text, JOB)
    assert director.role_level > country.role_level
    assert director.score > country.score
    assert any("Regional sales director" in item for item in director.differentiators)


def test_reference_business_ranking_is_explainable_and_distinct():
    candidates = [
        _candidate("John Anderson", "Regional Sales Director", "Textile"),
        _candidate("Sarah Lim", "Regional Key Account Director", "Apparel"),
        _candidate("David Nguyen", "Country Sales Manager", "Industrial/Textile"),
        _candidate("Emily Carter", "Retail Operations Manager", "Retail"),
        CandidateTextInput(
            filename="Michael Brown.txt",
            text="Michael Brown\nSoftware engineering leader. Cloud architecture DevOps Kubernetes Python AWS. English fluent.",
        ),
    ]
    output = RealRankingPipeline().run(RealRankingInput("job.txt", JOB, candidates))
    names = [item.candidate_name for item in output.ranked_candidates]
    scores = [item.fit_score for item in output.ranked_candidates]

    assert names == ["John Anderson", "Sarah Lim", "David Nguyen", "Emily Carter", "Michael Brown"]
    assert scores[0] > scores[1] > scores[2] > scores[3] > scores[4]
    assert output.ranked_candidates[0].differentiators
    assert output.ranked_candidates[1].comparative_breakdown["role_level"] > output.ranked_candidates[2].comparative_breakdown["role_level"]


def test_low_mission_fit_cannot_be_rescued_by_comparative_scope():
    engine = ComparativeRankingEngine()
    profile = engine.analyse(
        "Engineering Director",
        "Global Software Engineering Director managing 100 engineers across APAC. Kubernetes AWS DevOps.",
        JOB,
    )
    assert engine.adjusted_fit(12, profile) == 12
