from talentcopilot.interview.models import InterviewCompetency
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.technical_requirements import TechnicalRequirementService


SOFTWARE_JOB = """
Senior Backend Software Engineer
Requirements:
Strong proficiency in Python, FastAPI and PostgreSQL.
Experience with Docker, Kubernetes and CI/CD pipelines.
Design microservices and REST APIs. Build automated unit and integration testing.
Experience with AWS is preferred.
"""

FINANCE_JOB = """
Group Financial Controller
Required: strong knowledge of IFRS and group consolidation.
Lead monthly closing and statutory reporting.
Experience with SAP FI/CO and Power BI.
Own internal controls, audit readiness, budgeting and forecasting.
"""

SALES_JOB = """
Senior Sales Manager APAC
Proven experience in complex enterprise sales and strategic account growth.
Proficiency with Salesforce CRM, pipeline management and revenue forecasting.
Lead negotiations with C-level clients and channel partners across APAC.
Fluent English is essential.
"""

SUPPLY_JOB = """
Supply Chain Project Manager
Experience with S&OP, demand planning and inventory optimization.
Strong knowledge of SAP MM and warehouse management systems.
Lead supplier management, procurement and logistics improvement projects.
Apply Lean Six Sigma to reduce lead time and improve service level.
"""

MARKETING_JOB = """
Digital Marketing Manager
Expertise in SEO, Google Analytics 4 and paid media campaigns.
Manage customer acquisition, conversion optimization and CRM journeys.
Experience with HubSpot and marketing automation.
Build dashboards and report campaign ROI to leadership.
"""


def _names(job_title, text):
    catalog = TechnicalRequirementService().catalog(
        {"title": job_title, "raw_text": text}
    )
    return [item.name for item in catalog.requirements], catalog


def test_software_offer_extracts_exact_stack_without_hris_leakage(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    names, catalog = _names("Software Engineer", SOFTWARE_JOB)
    assert {"Python", "FastAPI", "PostgreSQL", "CI/CD"}.issubset(set(names))
    assert any("Testing" in name for name in names)
    assert not any("HRIS" in name or "SuccessFactors" in name for name in names)
    by_name = {item.name: item for item in catalog.requirements}
    assert by_name["PostgreSQL"].family == "Data & Databases"


def test_finance_offer_preserves_standard_platform_and_controls(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    names, catalog = _names("Financial Controller", FINANCE_JOB)
    assert "IFRS" in names
    assert "SAP FI/CO" in names
    assert "Power BI" in names
    assert "Financial Reporting & Consolidation" in names
    assert "Internal Controls & Compliance" in names
    by_name = {item.name: item for item in catalog.requirements}
    assert by_name["IFRS"].requirement_kind == "standard_or_regulation"
    assert not any("HRIS" in name for name in names)


def test_sales_offer_extracts_crm_pipeline_market_and_language_separately(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    names, catalog = _names("Senior Sales Manager APAC", SALES_JOB)
    assert "Salesforce CRM" in names
    assert "Pipeline & Revenue Forecasting" in names
    assert "APAC Market Experience" in names
    assert "Enterprise Sales & Account Growth" in names
    assert not any("English" in name for name in names)
    assert "Language: English" in catalog.eligibility_checks


def test_supply_chain_offer_extracts_erp_method_and_operations(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    names, _ = _names("Supply Chain Manager", SUPPLY_JOB)
    assert "SAP MM" in names
    assert "S&OP" in names
    assert "Lean Six Sigma" in names
    assert "Inventory & Logistics Optimisation" in names
    assert "Vendor & Stakeholder Management" in names
    assert not any("HRIS" in name for name in names)


def test_marketing_offer_extracts_tools_and_growth_capabilities(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    names, _ = _names("Digital Marketing Manager", MARKETING_JOB)
    assert "SEO" in names
    assert "Google Analytics 4" in names
    assert "HubSpot" in names
    assert "Digital Marketing & Acquisition" in names
    assert not any("HRIS" in name or "SAP" in name for name in names)


def test_candidate_evidence_is_contextual_across_unknown_products(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    service = TechnicalRequirementService()
    catalog = service.catalog({"title": "Software Engineer", "raw_text": SOFTWARE_JOB})
    requirements = {item.name: item for item in catalog.requirements}
    candidate = {
        "raw_text": (
            "Built Python backend services with Django and MySQL. "
            "Containerized applications with Docker and implemented unit tests."
        ),
        "skills": ["Python", "Django", "MySQL", "Docker"],
    }
    python = service.evaluate_candidate(requirements["Python"], candidate)
    postgres = service.evaluate_candidate(requirements["PostgreSQL"], candidate)
    docker = service.evaluate_candidate(requirements["Docker"], candidate)
    assert python.evidence_status in {"Direct evidence", "Ambiguous evidence"}
    assert docker.evidence_status == "Direct evidence"
    assert postgres.evidence_status == "Related evidence"
    assert any("mysql" in item.lower() for item in postgres.related_evidence)


def test_question_templates_are_generated_from_kind_and_family_not_domain_name():
    platform = InterviewCompetency(
        name="PostgreSQL",
        evidence_level="Medium",
        confidence=52,
        validate_in_interview=True,
        rationale="Related evidence only.",
        evidence_status="Related evidence",
        requirement_kind="technical_tool",
        requirement_family="Data & Databases",
        components=["PostgreSQL"],
        related_evidence=["MySQL"],
        importance="Critical",
    )
    question = InterviewQuestionService().build(
        [platform],
        role_title="Software Engineer",
        candidate={"skills": ["MySQL"], "raw_text": "Administered MySQL databases."},
        mission_requirements=["PostgreSQL"],
    )[0]
    assert "transferable" in question.question.lower()
    assert "postgresql" in question.question.lower()
    assert "mysql" in question.question.lower()


def test_hris_precision_pack_is_regression_protected(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    from tests.test_release_7_6_0_technical_requirement_intelligence import JOB_TEXT

    names, _ = _names("HRIS Manager", JOB_TEXT)
    assert names[:3] == [
        "SAP SuccessFactors & Core HR",
        "Power BI & HR Reporting",
        "AI Solutions for HR",
    ]
