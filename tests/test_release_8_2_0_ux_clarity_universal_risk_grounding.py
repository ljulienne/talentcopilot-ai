from pathlib import Path
from types import SimpleNamespace

from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.models.candidate_workspace import CandidateSkill
from talentcopilot.recruitment_reasoning import UniversalCandidateRiskGroundingEngine
from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService


ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")
TOPBAR_SOURCE = (ROOT / "talentcopilot/ui/app_shell.py").read_text(encoding="utf-8")
SIDEBAR_SOURCE = (ROOT / "talentcopilot/ui/premium_sidebar.py").read_text(encoding="utf-8")
WORKFLOW_SOURCE = (ROOT / "talentcopilot/ui/recruitment_workflow_shell.py").read_text(encoding="utf-8")
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
RISK_SOURCE = (ROOT / "talentcopilot/recruitment_reasoning/universal_risk_grounding.py").read_text(encoding="utf-8")
UPLOAD_SOURCE = (ROOT / "talentcopilot/services/recruitment_upload_session_service.py").read_text(encoding="utf-8")


def _skill(name: str, level: int) -> CandidateSkill:
    status = "Strong evidence" if level >= 80 else "Moderate evidence" if level >= 60 else "Limited evidence" if level >= 40 else "Not demonstrated"
    return CandidateSkill(
        name=name,
        level=level,
        status=status,
        evidence=f"Candidate-specific evidence for {name}",
        requirement_type="Role requirement",
    )


def test_job_title_and_location_are_separated_for_structured_documents():
    pipeline = JobIntelligencePipeline(extraction_mode="deterministic")
    analysis = pipeline.analyze_text(
        "offer.pdf",
        """HRIS MANAGER
Location :
Paris (75)
Job Description :
Position
Lead complex HRIS projects.
Minimum of 10 years of significant experience.
""",
    )
    assert analysis.role_profile.role_title == "HRIS Manager"
    assert analysis.role_profile.location == "Paris (75)"
    assert "Location" not in analysis.role_profile.role_title
    assert "role_extractor._infer_title(job_text, raw_role_title)" in UPLOAD_SOURCE
    assert '"location": job_location' in UPLOAD_SOURCE


def test_title_location_separation_is_not_hris_specific():
    pipeline = JobIntelligencePipeline(extraction_mode="deterministic")
    analysis = pipeline.analyze_text(
        "sales-role.pdf",
        """SENIOR SALES MANAGER
Location: Singapore
Job description
Lead enterprise sales across APAC.
""",
    )
    assert analysis.role_profile.role_title == "Senior Sales Manager"
    assert analysis.role_profile.location == "Singapore"


def test_universal_risk_engine_personalises_different_profiles_for_same_role():
    engine = UniversalCandidateRiskGroundingEngine()
    job = {
        "raw_text": "Python is required. System design is essential for this role.",
        "minimum_years_experience": 0,
    }
    candidate_a = engine.build(
        decision_report=None,
        skills=[_skill("Python", 90), _skill("System design", 28)],
        candidate={"years_experience": 8},
        job=job,
        achievements=["Reduced processing time by 35%"],
        candidate_text="Led Python delivery and reduced processing time by 35%.",
    )
    candidate_b = engine.build(
        decision_report=None,
        skills=[_skill("Python", 25), _skill("System design", 92)],
        candidate={"years_experience": 8},
        job=job,
        achievements=["Designed architecture used by 4 teams"],
        candidate_text="Owned system architecture used by 4 teams.",
    )

    assert candidate_a[0].related_requirement == "System design"
    assert candidate_b[0].related_requirement == "Python"
    assert candidate_a[0].title != candidate_b[0].title
    assert all(risk.title != "Personal ownership is unclear" for risk in [*candidate_a, *candidate_b])


def test_universal_risk_engine_supports_non_technical_job_families():
    engine = UniversalCandidateRiskGroundingEngine()
    risks = engine.build(
        decision_report=None,
        skills=[_skill("Enterprise negotiation", 34), _skill("Pipeline management", 86)],
        candidate={"years_experience": 9},
        job={"raw_text": "Enterprise negotiation is mandatory. Pipeline management is required."},
        achievements=["Increased regional revenue by 18%"],
        candidate_text="Managed a regional pipeline and increased revenue by 18%.",
    )
    assert risks[0].related_requirement == "Enterprise negotiation"
    assert "Enterprise negotiation" in risks[0].title


def test_risk_engine_is_domain_agnostic_and_contains_no_hris_fallbacks():
    for forbidden in (
        "SAP SuccessFactors",
        "Workday",
        "HRIS Manager",
        "Personal ownership is unclear",
    ):
        assert forbidden not in RISK_SOURCE
    assert "official Talent Fit scores and ranks" in RISK_SOURCE


def test_candidate_workspace_uses_rich_technical_requirements_without_recalculating_scores():
    service = CandidateWorkspaceService()
    analysis = SimpleNamespace(
        candidate_name="Generic Candidate",
        candidate_id="candidate-generic",
        official_match_score=73.0,
        match_score=73.0,
        official_rank=2,
        rank=2,
        score_breakdown={"mission_fit_rank": 2},
        decision_report=None,
    )
    report = service._build_one(
        analysis,
        {
            "name": "Generic Candidate",
            "skills": ["Stakeholder management"],
            "achievements": ["Improved adoption by 20%"],
            "years_experience": 7,
            "raw_text": "Led stakeholder adoption and improved adoption by 20%.",
        },
        {
            "required_skills": [],
            "technical_requirements": [
                {"name": "Stakeholder management", "importance": "High", "required_level": 4},
                {"name": "Budget governance", "importance": "Critical", "required_level": 4.5},
            ],
            "raw_text": "Budget governance is mandatory. Stakeholder management is required.",
        },
    )
    assert report.match_score == 73.0
    assert report.rank == 2
    assert any(skill.name == "Budget governance" for skill in report.skills)
    assert report.risks[0].related_requirement == "Budget governance"


def test_shell_exposes_one_page_owned_recommended_action_and_no_app_health():
    assert "_render_import_health" not in APP_SOURCE
    assert 'expander("App health")' not in APP_SOURCE
    assert "premium_sidebar_next_action" not in SIDEBAR_SOURCE
    assert 'key="workflow_continue' not in WORKFLOW_SOURCE
    assert "the page below contains the single contextual action" in WORKFLOW_SOURCE


def test_top_command_bar_has_balanced_horizontal_hierarchy():
    for marker in (
        "tc-topbar-eyebrow",
        "tc-topbar-search-marker",
        "tc-topbar-copilot-marker",
        "title_col, search_col, mission_col, copilot_col",
        "Talent intelligence workspace",
    ):
        assert marker in TOPBAR_SOURCE
    css = THEME_SOURCE.split("Release 8.2.0 — UX clarity and unified command bar", 1)[1]
    assert "linear-gradient(118deg" in css
    assert "tc-topbar-copilot-marker" in css
    assert "tc-topbar-search-marker" in css
