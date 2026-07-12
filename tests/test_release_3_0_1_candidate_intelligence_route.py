import importlib

import pytest

from talentcopilot.services.candidate_intelligence import (
    CandidateIntelligenceService,
)
from talentcopilot.services.candidate_workspace_service import (
    CandidateWorkspaceService,
)
from talentcopilot.services.demo_session_factory import (
    create_demo_recruitment_session,
)
from talentcopilot.ui.enterprise_navigation import (
    get_enterprise_navigation,
)


def _candidate_intelligence_routes():
    routes = []

    for section in get_enterprise_navigation().values():
        for page in section.pages:
            if page.label == "Candidate Intelligence":
                routes.append(page)

    return routes


def test_candidate_intelligence_route_uses_official_workspace():
    routes = _candidate_intelligence_routes()

    assert len(routes) == 1

    route = routes[0]

    assert route.module == "talentcopilot.ui.candidate_workspace"
    assert route.function == "render_candidate_workspace"

    module = importlib.import_module(route.module)
    assert callable(getattr(module, route.function))


def test_candidate_intelligence_uses_official_david_smith_score():
    session = create_demo_recruitment_session()

    official_analysis = next(
        analysis
        for analysis in session.ranked_analyses
        if analysis.candidate_name == "David Smith"
    )

    reports = CandidateWorkspaceService().build_all(session)

    report = next(
        item
        for item in reports
        if item.candidate_id == official_analysis.candidate_id
    )

    snapshot = CandidateIntelligenceService().build(report)

    assert snapshot.mission_fit == pytest.approx(
        official_analysis.match_score
    )
    assert report.match_score == pytest.approx(
        official_analysis.match_score
    )
    assert report.rank == official_analysis.rank

    # Regression guard: the legacy Decision Core value must not return.
    assert snapshot.mission_fit != pytest.approx(41.0)


def test_all_candidate_intelligence_scores_match_official_session():
    session = create_demo_recruitment_session()

    reports = CandidateWorkspaceService().build_all(session)

    reports_by_id = {
        report.candidate_id: report
        for report in reports
    }

    for analysis in session.ranked_analyses:
        report = reports_by_id[analysis.candidate_id]
        snapshot = CandidateIntelligenceService().build(report)

        assert report.match_score == pytest.approx(
            analysis.match_score
        )
        assert report.rank == analysis.rank
        assert snapshot.mission_fit == pytest.approx(
            analysis.match_score
        )
