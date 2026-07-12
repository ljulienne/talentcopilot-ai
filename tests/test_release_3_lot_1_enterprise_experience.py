from talentcopilot.models.mission import MissionCanvas, MissionDomain
from talentcopilot.services.mission_intelligence import understand_mission


def test_recruitment_mission_builds_explainable_canvas():
    canvas = understand_mission(
        "We need to recruit a Global HRIS Director within three months. "
        "International transformation experience is mandatory."
    )

    assert isinstance(canvas, MissionCanvas)
    assert canvas.domain is MissionDomain.RECRUITMENT
    assert canvas.target_page == "Recruitment Workspace"
    assert "Job description" in canvas.required_inputs[0]
    assert len(canvas.recommended_workflow) >= 5
    assert "Mandatory criteria mentioned" in canvas.constraints
    assert "Time constraint detected" in canvas.constraints
    assert "International scope detected" in canvas.constraints
    assert canvas.confidence in {"Medium", "High"}


def test_collaboration_mission_is_data_honest():
    canvas = understand_mission(
        "I want an ONA to understand collaboration silos between departments."
    )

    assert canvas.domain is MissionDomain.COLLABORATION
    assert "Relationship survey" in canvas.required_inputs[0]
    assert canvas.target_page == "Organization Intelligence"
    assert "relational evidence" in canvas.objective.lower()


def test_unknown_mission_requests_clarification():
    canvas = understand_mission("Help me improve things")

    assert canvas.domain is MissionDomain.UNKNOWN
    assert canvas.target_page is None
    assert canvas.confidence == "Limited"
    assert "Clarify" in canvas.mission_title


def test_empty_mission_is_safe():
    canvas = understand_mission("   ")

    assert canvas.domain is MissionDomain.UNKNOWN
    assert canvas.raw_request == ""
    assert canvas.recommended_workflow
