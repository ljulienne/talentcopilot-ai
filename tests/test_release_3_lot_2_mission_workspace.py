from talentcopilot.models.mission import MissionDomain
from talentcopilot.models.mission_workspace import MissionHealth
from talentcopilot.services.mission_intelligence import understand_mission
from talentcopilot.services.mission_workspace import build_mission_workspace
from talentcopilot.ui.mission_workspace import render_mission_workspace


class _Session:
    candidate_count = 4
    analyzed_count = 3
    candidates = ({"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"})


def test_mission_workspace_is_importable():
    assert callable(render_mission_workspace)


def test_workspace_uses_real_recruitment_progress():
    canvas = understand_mission("Recruit a global HRIS Director within three months")
    snapshot = build_mission_workspace(canvas, _Session())
    assert canvas.domain is MissionDomain.RECRUITMENT
    assert snapshot.stage == "Candidate analysis in progress"
    assert snapshot.readiness >= 70
    assert snapshot.decision_confidence >= 70
    assert snapshot.health in {MissionHealth.STRONG, MissionHealth.NEEDS_ATTENTION}
    assert snapshot.journal[-1].label == "Candidate analysis"


def test_workspace_without_project_is_honest_about_missing_evidence():
    canvas = understand_mission("Prepare succession for our CFO")
    snapshot = build_mission_workspace(canvas)
    assert snapshot.readiness < 60
    assert snapshot.missing_evidence
    assert snapshot.next_actions
    assert "never" not in snapshot.reasoning.lower()


def test_scores_describe_decision_not_people():
    canvas = understand_mission("Recruit a payroll manager")
    snapshot = build_mission_workspace(canvas)
    assert "Neither score evaluates a person" in snapshot.reasoning
