from talentcopilot.interview.models import InterviewCompetency
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.technical_requirements import TechnicalRequirementService
from talentcopilot.technical_requirements.models import TechnicalRequirement


REAL_HRIS_JOB = """
HRIS MANAGER
Location Paris, FRANCE
About LVMH Fashion Group: iconic Maisons and luxury brands.
Job responsibilities
Main Responsibilities:
HRIS Project Management:
Lead and coordinate complex HRIS projects (implementation of new modules,
system migration, process optimization, implementation of interfaces with third-party systems).
Support the deployment of Core HR.
Participate actively in the development of Artificial Intelligence (AI) solutions aimed at optimizing HR processes.
Define functional and technical requirements with HR teams and solution providers.
Ensure functional and technical acceptance testing of implemented solutions.
HRIS & Data Functional Expertise:
Provide expertise on market HRIS solutions and best practices (SAP SuccessFactors).
Carry out data cleaning and data reliability actions within Core HR.
Design and implement dynamic Power BI reports from Core HR data.
Actively participate in the ICR (Individual Compensation Review) campaign by providing HRIS expertise.
Change Management:
Provide post-deployment support and upskilling for teams.
External Providers Management:
Manage relationships with HRIS solution providers and integrators.
Minimum of 10 years of HRIS project management in an international environment.
Higher education degree (Bac+5).
"""

LOUIS_GROUNDED = """
LOUIS JULIENNE
HR Projects and Digitization
+689 89 51 71 74
https://www.linkedin.com/in/louisjulienne/
louisjulienne1987@gmail.com
Papeete, French-Polynesia
China Regional HR IT Manager
Interplex Metalforming
Implemented SeditWeb2 HRIS and integrated it with Octime to optimize HR and payroll workflows.
Implemented and upgraded TAPPLENT HRIS, including onboarding, recruitment and performance modules.
Launched Microsoft Power BI for China HR Teams and ensured HR data accuracy and integrity.
Led the development and launch of HRIS covering Employee Data, Reporting, Performance and Salary Review modules.
Led an HRIS system project and liaised with vendors.
Hired, led and developed one team member while managing HRIS projects.
IBM Data Science Professional Certificate.
"""


def _catalog():
    return TechnicalRequirementService().catalog(
        {"title": "HRIS Manager", "raw_text": REAL_HRIS_JOB}
    )


def test_real_offer_catalog_filters_marketing_eligibility_and_heading_noise(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    catalog = _catalog()
    names = [item.name for item in catalog.requirements]

    expected = {
        "SAP SuccessFactors & Core HR",
        "Power BI & HR Reporting",
        "AI Solutions for HR",
        "HRIS Project Leadership",
        "Interfaces & Technical Delivery",
        "Data Quality & Core HR Reliability",
        "Change Management & Adoption",
        "Vendor & Stakeholder Management",
        "Team Leadership & International Delivery",
        "Individual Compensation Review (ICR)",
    }
    assert expected.issubset(set(names))
    assert not any("LVMH" in name or "Fashion Group" in name for name in names)
    assert not any("Bac+5" in name or "Location" in name for name in names)
    assert not any(name in {"Data Functional", "market HRIS solutions", "ICR", "Individual Compensation"} for name in names)


def test_successfactors_related_evidence_is_full_grounded_professional_source(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    service = TechnicalRequirementService()
    requirement = next(item for item in _catalog().requirements if item.name == "SAP SuccessFactors & Core HR")
    evidence = service.evaluate_candidate(requirement, {"raw_text": LOUIS_GROUNDED})

    assert evidence.evidence_status == "Related evidence"
    assert evidence.related_evidence
    joined = " ".join(evidence.related_evidence)
    assert "Implemented SeditWeb2 HRIS" in joined or "Implemented and upgraded TAPPLENT HRIS" in joined
    forbidden = ("gmail.com", "linkedin", "LOUIS JULIENNE", "French-Polynesia", "China Regional HR IT Manager")
    assert not any(value.lower() in joined.lower() for value in forbidden)


def test_contact_and_job_title_only_are_not_transferable_evidence():
    requirement = TechnicalRequirement(
        requirement_id="successfactors",
        name="SAP SuccessFactors",
        category="Technology & HRIS",
        family="HRIS Platforms",
        requirement_kind="technical_platform",
        importance="Critical",
        required_level=4.5,
        aliases=("SAP SuccessFactors",),
        components=("SAP SuccessFactors",),
    )
    candidate = {
        "raw_text": """
        LOUIS JULIENNE
        HR IT Manager
        louisjulienne1987@gmail.com
        https://www.linkedin.com/in/louisjulienne/
        Papeete, French-Polynesia
        """
    }
    evidence = TechnicalRequirementService().evaluate_candidate(requirement, candidate)
    assert evidence.evidence_status == "No direct evidence"
    assert evidence.related_evidence == ()
    assert "sufficiently grounded" in evidence.evidence


def test_compensation_review_uses_salary_review_as_related_source(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    service = TechnicalRequirementService()
    requirement = next(item for item in _catalog().requirements if item.name == "Individual Compensation Review (ICR)")
    evidence = service.evaluate_candidate(requirement, {"raw_text": LOUIS_GROUNDED})

    assert evidence.evidence_status == "Related evidence"
    assert len(evidence.related_evidence) == 1
    assert "Salary Review" in evidence.related_evidence[0]
    assert evidence.related_evidence[0].startswith("Led the development")


def test_power_bi_direct_evidence_prefers_action_sentence(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    service = TechnicalRequirementService()
    requirement = next(item for item in _catalog().requirements if item.name == "Power BI & HR Reporting")
    candidate = {
        "raw_text": LOUIS_GROUNDED + "\nSYSTEMS & TOOLS\nTABLEAU, MICROSOFT POWER BI, QLIKSENSE",
        "skills": ["Power BI"],
    }
    evidence = service.evaluate_candidate(requirement, candidate)
    assert evidence.evidence_status == "Direct evidence"
    assert evidence.evidence.startswith("Launched Microsoft Power BI")
    assert evidence.related_evidence == ()


def test_ai_related_evidence_prefers_data_science_credential(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    service = TechnicalRequirementService()
    requirement = next(item for item in _catalog().requirements if item.name == "AI Solutions for HR")
    evidence = service.evaluate_candidate(requirement, {"raw_text": LOUIS_GROUNDED})
    assert evidence.evidence_status == "Related evidence"
    assert "Data Science Professional Certificate" in evidence.related_evidence[0]


def test_vendor_sentence_with_liaising_is_direct_evidence(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    service = TechnicalRequirementService()
    requirement = next(item for item in _catalog().requirements if item.name == "Vendor & Stakeholder Management")
    evidence = service.evaluate_candidate(requirement, {"raw_text": LOUIS_GROUNDED})
    assert evidence.evidence_status == "Direct evidence"
    assert "liaised with vendors" in evidence.evidence.lower()


def test_unknown_database_transfer_keeps_source_sentence_not_detached_entity():
    requirement = TechnicalRequirement(
        requirement_id="postgresql",
        name="PostgreSQL",
        category="Data & Analytics",
        family="Data & Databases",
        requirement_kind="technical_tool",
        importance="Critical",
        required_level=4.0,
        aliases=("PostgreSQL",),
        components=("PostgreSQL",),
    )
    candidate = {"raw_text": "Built and administered MySQL databases for a high-volume commerce platform."}
    evidence = TechnicalRequirementService().evaluate_candidate(requirement, candidate)
    assert evidence.evidence_status == "Related evidence"
    assert evidence.related_evidence == (
        "Built and administered MySQL databases for a high-volume commerce platform.",
    )


def test_old_770_embedded_catalog_is_regenerated(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_REQUIREMENT_MODE", "deterministic")
    catalog = TechnicalRequirementService().catalog(
        {
            "title": "HRIS Manager",
            "raw_text": REAL_HRIS_JOB,
            "technical_requirement_engine_version": "7.7.0",
            "technical_requirements": [
                {"name": "About LVMH & Core HR", "family": "HRIS Platforms"}
            ],
        }
    )
    assert "About LVMH & Core HR" not in [item.name for item in catalog.requirements]
    assert "SAP SuccessFactors & Core HR" in [item.name for item in catalog.requirements]


def test_interview_question_quotes_grounded_related_source():
    competency = InterviewCompetency(
        name="PostgreSQL",
        evidence_level="Medium",
        confidence=52,
        validate_in_interview=True,
        rationale="Related evidence.",
        evidence_status="Related evidence",
        requirement_kind="technical_tool",
        requirement_family="Data & Databases",
        components=["PostgreSQL"],
        related_evidence=["Built and administered MySQL databases for a commerce platform."],
        importance="Critical",
    )
    question = InterviewQuestionService().build(
        [competency], role_title="Backend Engineer", mission_requirements=["PostgreSQL"]
    )[0]
    assert "grounded adjacent evidence" in question.question.lower()
    assert "mysql databases" in question.question.lower()
