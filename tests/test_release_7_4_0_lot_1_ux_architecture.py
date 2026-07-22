from talentcopilot.services.recruitment_experience_architecture import (
    DUPLICATE_CONTENT_CONTRACT,
    LEGACY_ROUTE_ALIASES,
    TARGET_SPACES,
    WORKFLOW,
    validate_architecture,
)


def test_target_architecture_is_valid():
    assert validate_architecture() == []


def test_target_architecture_has_four_primary_spaces():
    assert [space.label for space in TARGET_SPACES] == [
        "Recruitment Workspace",
        "Candidate Intelligence",
        "Interview Intelligence",
        "Comparison & Decision",
    ]


def test_workflow_is_complete_and_ordered():
    assert len(WORKFLOW) == 9
    assert WORKFLOW[0].key == "setup"
    assert WORKFLOW[-1].key == "decide"
    assert all(step.target_page for step in WORKFLOW)


def test_each_information_type_has_one_owner():
    assert DUPLICATE_CONTENT_CONTRACT["competency matrix"] == "Candidate Intelligence"
    assert DUPLICATE_CONTENT_CONTRACT["interview questions"] == "Interview Intelligence"
    assert DUPLICATE_CONTENT_CONTRACT["final decision"] == "Decision Board"


def test_legacy_routes_have_explicit_aliases():
    assert LEGACY_ROUTE_ALIASES["Candidate Workspace"] == "Candidate Intelligence"
    assert LEGACY_ROUTE_ALIASES["Interview Workspace"] == "Interview Intelligence"
