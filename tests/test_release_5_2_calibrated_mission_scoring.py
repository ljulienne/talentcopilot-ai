from talentcopilot.calibrated_scoring import CalibratedMissionScoringEngine
from talentcopilot.comparative_ranking import ComparativeRankingEngine
from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline

JOB = """Senior Sales Manager APAC
12+ years B2B textile/apparel sales. 5+ years regional leadership.
Own an USD 80M+ business, manage country sales managers, multinational brands.
SAP Salesforce Power BI. English mandatory; Mandarin preferred.
"""


def candidate(name, title, industry):
    return CandidateTextInput(filename=f"{name}.txt", text=f"""{name}
Experienced {title} with a background in {industry}.
Professional Experience 2012-2026
Led regional planning and commercial strategy across APAC.
Managed teams of 15-40 employees. Owned budgets, forecasts and strategic accounts.
Negotiated multi-million-dollar contracts. Business development and pricing.
SAP Salesforce Power BI. English fluent. MBA.
""")


def benchmark():
    return [
        candidate("John Anderson", "Regional Sales Director", "Textile"),
        candidate("Sarah Lim", "Regional Key Account Director", "Apparel"),
        candidate("David Nguyen", "Country Sales Manager", "Industrial/Textile"),
        candidate("Emily Carter", "Retail Operations Manager", "Retail"),
        CandidateTextInput(filename="Michael Brown.txt", text="Michael Brown\nSoftware engineering leader. Cloud architecture DevOps Kubernetes Python AWS. English fluent."),
    ]


def test_calibrated_benchmark_order_and_business_ranges():
    output = RealRankingPipeline().run(RealRankingInput("job.txt", JOB, benchmark()))
    names = [item.candidate_name for item in output.ranked_candidates]
    scores = {item.candidate_name: item.fit_score for item in output.ranked_candidates}
    assert names == ["John Anderson", "Sarah Lim", "David Nguyen", "Emily Carter", "Michael Brown"]
    assert 90 <= scores["John Anderson"] <= 96
    assert 76 <= scores["Sarah Lim"] <= 85
    assert 58 <= scores["David Nguyen"] <= 70
    assert 28 <= scores["Emily Carter"] <= 42
    assert 0 <= scores["Michael Brown"] <= 12


def test_calibration_uses_scope_not_candidate_name():
    comparison = ComparativeRankingEngine()
    calibration = CalibratedMissionScoringEngine()
    a = comparison.analyse("A", candidate("A", "Regional Sales Director", "Textile").text, JOB)
    b = comparison.analyse("B", candidate("B", "Country Sales Manager", "Textile").text, JOB)
    breakdown = {"industry": 100, "function": 100, "experience": 100}
    score_a = calibration.calibrate(mission_fit=98, mission_breakdown=breakdown, comparative=a, differentiators=a.differentiators, validation_points=a.validation_points)
    score_b = calibration.calibrate(mission_fit=98, mission_breakdown=breakdown, comparative=b, differentiators=b.differentiators, validation_points=b.validation_points)
    assert score_a.score > score_b.score
    assert score_a.band == "Excellent Fit"
    assert score_b.critical_cap <= 70


def test_calibrated_confidence_is_distinct_from_match_score():
    output = RealRankingPipeline().run(RealRankingInput("job.txt", JOB, benchmark()))
    values = [(item.fit_score, item.confidence_score) for item in output.ranked_candidates]
    assert any(score != confidence for score, confidence in values)
    assert all(50 <= confidence <= 97 for _, confidence in values)
