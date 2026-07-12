from talentcopilot.ui.executive_briefing import (
    build_briefing_domains,
    build_priorities,
    render_executive_briefing,
)
from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_page_by_label


class DemoSession:
    role_title = "Transformation Lead"
    candidate_count = 3
    analyzed_count = 3


def test_executive_briefing_is_importable():
    assert callable(render_executive_briefing)


def test_briefing_exposes_six_business_diagnostics():
    domains = build_briefing_domains(DemoSession())
    assert [domain.key for domain in domains] == [
        "hire", "organize", "plan", "develop", "connect", "protect"
    ]
    assert domains[0].status == "Ready"
    assert domains[4].status == "ONA data required"


def test_briefing_is_data_aware_without_session():
    domains = build_briefing_domains(None)
    assert domains[0].status == "Start here"
    assert "required" in domains[0].metric.lower()
    assert build_priorities(None)


def test_command_center_is_removed_from_primary_navigation():
    labels = [page.label for page in flatten_enterprise_pages()]
    assert "Executive Brief" in labels
    assert "Recruitment Command Center" not in labels
    legacy_page = get_page_by_label("Recruitment Command Center")
    assert legacy_page is not None
    assert legacy_page.module == "talentcopilot.ui.command_center"
