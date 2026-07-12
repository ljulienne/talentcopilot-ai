import importlib

from talentcopilot.ui.enterprise_navigation import (
    get_enterprise_navigation,
)


def _candidate_intelligence_pages():
    pages = []

    for section in get_enterprise_navigation().values():
        for page in section.pages:
            if page.label == "Candidate Intelligence":
                pages.append(page)

    return pages


def test_candidate_workspace_v2_navigation():
    """
    Regression guard for Release 3.0.1.

    The historical Candidate Workspace v2 route was removed because it
    calculated a second fit score through the Decision Core.

    Candidate Intelligence must now use the official Candidate Workspace,
    which consumes RecruitmentSession.ranked_analyses.
    """
    pages = _candidate_intelligence_pages()

    assert len(pages) == 1

    page = pages[0]

    assert page.module == "talentcopilot.ui.candidate_workspace"
    assert page.function == "render_candidate_workspace"

    module = importlib.import_module(page.module)
    assert callable(getattr(module, page.function))
