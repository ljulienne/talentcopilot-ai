import json

from talentcopilot.mission_fit_v2 import MissionFitEngineV2
from talentcopilot.real_matching.models import RealMatchingInput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline


JOB = """
Senior Sales Manager APAC - textile and apparel. Minimum 12 years B2B sales
experience and 5 years regional leadership. Lead an USD 80M business across
APAC. SAP, Salesforce, Power BI, forecasting, pricing and negotiation required.
MBA and Mandarin preferred.
"""


def test_mission_fit_v2_separates_relevant_and_adjacent_profiles():
    engine = MissionFitEngineV2()
    textile_sales = engine.evaluate(
        JOB,
        "David Nguyen Country Sales Manager APAC textile apparel. 15 years B2B sales. Managed a team of 25. Revenue, P&L, forecasting, pricing, negotiation. SAP Salesforce Power BI. MBA English.",
        "David Nguyen",
    )
    retail_operations = engine.evaluate(
        JOB,
        "Emily Carter Retail Operations Manager Asia. 14 years operations and store leadership. Managed teams. SAP Power BI budgeting and forecasting. English.",
        "Emily Carter",
    )
    software = engine.evaluate(
        JOB,
        "Michael Brown Software Engineering Manager. 15 years cloud DevOps microservices. Led a team of engineers. AWS Kubernetes.",
        "Michael Brown",
    )

    assert textile_sales.overall_score > retail_operations.overall_score
    assert retail_operations.overall_score > software.overall_score
    assert textile_sales.overall_score - software.overall_score >= 35
    assert textile_sales.breakdown["industry"] == 100
    assert software.breakdown["function"] == 0


def test_mission_fit_v2_outputs_explainable_dimensions_and_distinct_rationale():
    result = MissionFitEngineV2().evaluate(
        JOB,
        "Sarah Lim Regional Key Account Director apparel APAC. 13 years B2B sales. Salesforce, SAP, negotiation and forecasting. English Mandarin.",
        "Sarah Lim",
    )
    assert len(result.dimensions) == 8
    assert result.evidence
    assert "Sarah Lim" in result.rationale
    assert result.recommendation in {"Strong Hire", "Interview", "More Evidence Required", "Review", "Reject"}


def test_real_matching_pipeline_promotes_mission_fit_v2_to_canonical_profile():
    output = RealMatchingPipeline().run(
        RealMatchingInput(
            candidate_filename="david.txt",
            candidate_text="David Nguyen\nCountry Sales Manager APAC textile apparel. 15 years B2B sales. SAP Salesforce Power BI. Managed a team of 20. Forecasting pricing negotiation MBA English.",
            job_filename="job.txt",
            job_text=JOB,
        )
    )
    profile = output.decision_output.profile
    assert profile.metadata["mission_fit_engine"] == "mission-fit-v2.0"
    assert float(profile.metadata["fit_score"]) == profile.fit_score
    assert json.loads(profile.metadata["mission_fit_breakdown"])["industry"] == 100
    assert json.loads(profile.metadata["mission_fit_evidence"])
