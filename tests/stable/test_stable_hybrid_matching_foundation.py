from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput
from talentcopilot.services.hybrid_intelligence_demo_service import HybridIntelligenceDemoService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_hybrid_matching_engine_semantic_score():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Vincent Blakoe",
            role_title="HRIS Manager",
            candidate_skills=["SIRH", "OCTIME", "Business Objects"],
            required_skills=["HRIS", "Time Management", "Reporting"],
        )
    )

    assert report.semantic_score >= 70
    assert report.semantic_skill_report.covered_skills == 3


def test_hybrid_intelligence_demo_service():
    demo = HybridIntelligenceDemoService().run_demo()

    assert demo.report.candidate_name
    assert demo.report.semantic_score >= 70


def test_hybrid_intelligence_ui_imports():
    module = __import__("talentcopilot.ui.hybrid_intelligence", fromlist=["render_hybrid_intelligence"])
    assert hasattr(module, "render_hybrid_intelligence")


def test_hybrid_intelligence_navigation():
    page = get_page_by_label("Hybrid Intelligence")
    assert page is not None
    assert page.module == "talentcopilot.ui.hybrid_intelligence"
