from talentcopilot.services.talent_intelligence_service import TalentIntelligenceService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_talent_intelligence_empty_report():
    report = TalentIntelligenceService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.shortlist == []
    assert report.recommendations


def test_talent_intelligence_imports():
    module = __import__("talentcopilot.ui.talent_intelligence", fromlist=["render_talent_intelligence"])
    assert hasattr(module, "render_talent_intelligence")


def test_talent_intelligence_navigation():
    page = get_page_by_label("Talent Intelligence")
    assert page is not None
    assert page.module == "talentcopilot.ui.talent_intelligence"
    assert page.function == "render_talent_intelligence"
