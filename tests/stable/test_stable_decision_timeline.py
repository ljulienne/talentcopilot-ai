import pytest

from talentcopilot.intelligence_core.engine import DecisionEngine, InsightEngine
from talentcopilot.intelligence_core.models import DecisionStatus
from talentcopilot.intelligence_core.timeline_engine import DecisionTimelineEngine
from talentcopilot.ui.decision_timeline import timeline_dataframe


def _queue():
    insight = InsightEngine().build(
        insight_id="knowledge-payroll",
        title="Payroll knowledge concentration",
        category="Knowledge",
        severity="High",
        confidence=0.9,
        current_situation="One employee holds the critical payroll knowledge.",
        business_impact="Payroll continuity is exposed.",
        evidence=[
            {"label": "Experts", "detail": "1", "strength": 1.0},
            {"label": "Backups", "detail": "0", "strength": 0.9},
        ],
        recommendations=[
            {
                "action": "Train two payroll backups",
                "priority": "Immediate",
                "timeframe": "30 days",
                "business_value": "Protect payroll continuity",
            }
        ],
    )
    return DecisionEngine().generate([insight])


def test_timeline_initializes_proposed_decisions():
    timeline = DecisionTimelineEngine().initialize(_queue(), occurred_at="2026-07-11T00:00:00+00:00")
    assert timeline.proposed_count == 1
    assert timeline.active_count == 0
    assert timeline.completion_rate == 0
    assert timeline.items[0].current_status == DecisionStatus.PROPOSED


def test_timeline_tracks_valid_progression():
    engine = DecisionTimelineEngine()
    timeline = engine.initialize(_queue(), occurred_at="2026-07-11T00:00:00+00:00")
    decision_id = timeline.items[0].decision.decision_id
    timeline = engine.transition(
        timeline,
        decision_id=decision_id,
        status=DecisionStatus.ACCEPTED,
        occurred_at="2026-07-12T00:00:00+00:00",
    )
    timeline = engine.transition(
        timeline,
        decision_id=decision_id,
        status=DecisionStatus.IN_PROGRESS,
        occurred_at="2026-07-13T00:00:00+00:00",
    )
    timeline = engine.transition(
        timeline,
        decision_id=decision_id,
        status=DecisionStatus.COMPLETED,
        note="Two backups trained.",
        occurred_at="2026-07-20T00:00:00+00:00",
    )
    assert timeline.completed_count == 1
    assert timeline.completion_rate == 100
    assert len(timeline.items[0].events) == 4


def test_timeline_rejects_invalid_transition():
    engine = DecisionTimelineEngine()
    timeline = engine.initialize(_queue())
    with pytest.raises(ValueError):
        engine.transition(
            timeline,
            decision_id=timeline.items[0].decision.decision_id,
            status=DecisionStatus.COMPLETED,
        )


def test_timeline_export_contract():
    timeline = DecisionTimelineEngine().initialize(_queue(), occurred_at="2026-07-11T00:00:00+00:00")
    frame = timeline_dataframe(timeline)
    assert not frame.empty
    assert {"decision", "priority", "status", "occurred_at", "actor", "note"}.issubset(frame.columns)
