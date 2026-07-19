from talentcopilot.mission_fit_v2 import MissionFitEngineV2
from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline


HRIS_JOB = """
Senior HRIS Project Manager
Minimum 8 years experience. Lead HRIS transformation and implementation.
Required: HRIS, project management, stakeholder management, payroll, time
management, reporting, integrations and change management. Workday or
SuccessFactors preferred. English required.
"""


def _run(job, candidates):
    return RealRankingPipeline().run(
        RealRankingInput(
            job_filename="job.txt",
            job_text=job,
            candidates=[
                CandidateTextInput(filename=f"{name}.txt", text=text)
                for name, text in candidates
            ],
        )
    )


def test_hris_profiles_are_meaningfully_separated():
    output = _run(HRIS_JOB, [
        (
            "Strong HRIS",
            "Strong HRIS\n12 years experience as Senior HRIS Project Manager. "
            "Led Workday and SuccessFactors implementations, payroll and time "
            "management integrations, reporting, stakeholder management and "
            "change management. English.",
        ),
        (
            "Adjacent HR",
            "Adjacent HR\n10 years experience as HR Business Partner. "
            "Change management, stakeholder management, recruitment and training. English.",
        ),
        (
            "Reporting Analyst",
            "Reporting Analyst\n7 years experience in Excel, Power BI, reporting and data analysis.",
        ),
        (
            "Graphic Designer",
            "Graphic Designer\n8 years experience in branding, Adobe and graphic design.",
        ),
    ])

    scores = {item.candidate_name.casefold(): item.fit_score for item in output.ranked_candidates}
    names = [item.candidate_name for item in output.ranked_candidates]

    assert names[0].casefold() == "Strong HRIS".casefold()
    assert scores["Strong HRIS".casefold()] >= 70
    assert scores["Strong HRIS".casefold()] > scores["Adjacent HR".casefold()] + 15
    assert scores["Adjacent HR".casefold()] > scores["Graphic Designer".casefold()]
    assert len(set(scores.values())) >= 3


def test_same_candidates_reorder_when_job_family_changes():
    candidates = [
        (
            "Alice Martin",
            "Alice Martin\nHRIS Lead with 10 years HRIS Workday payroll "
            "integrations project management and change management.",
        ),
        (
            "Benjamin Carter",
            "Benjamin Carter\nSales Lead with 10 years B2B sales, key accounts, "
            "pricing, forecasting, negotiation and revenue ownership.",
        ),
        (
            "Daniel Kim",
            "Daniel Kim\nSoftware Engineering Manager with 10 years software "
            "engineering, Python, cloud APIs and DevOps.",
        ),
    ]

    hris = _run(HRIS_JOB, candidates)
    sales = _run(
        "Senior Sales Manager. Minimum 8 years B2B sales, pricing, forecasting, negotiation and key accounts.",
        candidates,
    )
    engineering = _run(
        "Software Engineering Manager. Minimum 8 years software engineering, Python, cloud, APIs and DevOps.",
        candidates,
    )

    assert hris.ranked_candidates[0].candidate_name.casefold() == "Alice Martin".casefold()
    assert sales.ranked_candidates[0].candidate_name.casefold() == "Benjamin Carter".casefold()
    assert engineering.ranked_candidates[0].candidate_name.casefold() == "Daniel Kim".casefold()


def test_french_hris_vocabulary_is_supported():
    result = MissionFitEngineV2().evaluate(
        "Responsable SIRH. Minimum 8 ans. Gestion de projet, paie, GTA, "
        "reporting, interfaces et conduite du changement.",
        "Chef de projet SIRH avec 11 ans d'expérience. Paie, OCTIME GTA, "
        "Business Objects, interfaces API et conduite du changement.",
        "Candidate",
    )
    assert result.overall_score >= 65
    assert result.breakdown["function"] == 100
    assert result.breakdown["business_scope"] >= 70


def test_clear_no_fit_remains_low():
    result = MissionFitEngineV2().evaluate(
        HRIS_JOB,
        "Graphic Designer\n8 years branding, illustration and Adobe Creative Suite.",
        "Graphic Designer",
    )
    assert result.overall_score < 40
    assert result.recommendation == "Reject"


def test_sales_manager_reference_order_is_preserved():
    job = """Senior Sales Manager APAC
    12+ years B2B textile/apparel sales. 5+ years regional leadership.
    Own an USD 80M+ business, manage country sales managers, multinational brands.
    SAP Salesforce Power BI. English mandatory; Mandarin preferred."""
    candidates = [
        ("John Anderson", "John Anderson Regional Sales Director Textile APAC. 14 years B2B sales. Managed teams of 40. Owned budgets forecasts strategic accounts pricing P&L. SAP Salesforce Power BI English MBA."),
        ("Sarah Lim", "Sarah Lim Regional Key Account Director Apparel APAC. 13 years B2B sales. Managed teams of 20. Forecasting strategic accounts pricing negotiation. SAP Salesforce English Mandarin."),
        ("David Nguyen", "David Nguyen Country Sales Manager Textile. 13 years B2B sales. Managed a team of 10. Forecasting pricing negotiation. SAP English."),
        ("Emily Carter", "Emily Carter Retail Operations Manager. 14 years retail operations. Managed teams. SAP Power BI budgeting."),
        ("Michael Brown", "Michael Brown Software Engineering Manager. 15 years cloud DevOps Kubernetes Python AWS."),
    ]
    output = _run(job, candidates)
    assert [item.candidate_name for item in output.ranked_candidates] == [
        "John Anderson", "Sarah Lim", "David Nguyen", "Emily Carter", "Michael Brown"
    ]


def test_pipeline_versions_are_exposed():
    output = _run(HRIS_JOB, [
        ("Candidate", "Candidate\n10 years HRIS Workday project management payroll reporting.")
    ])
    profile = output.ranked_candidates[0].matching_output.decision_output.profile
    assert profile.metadata["mission_fit_engine"] == "mission-fit-v2.0"
    assert profile.metadata["calibrated_scoring_engine"] == "calibrated-mission-scoring-v1.1-universal"
    assert profile.metadata["comparative_ranking_engine"] == "comparative-ranking-v1.1-universal"
