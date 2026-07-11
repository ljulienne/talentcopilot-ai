from talentcopilot.intelligence_core.engine import DecisionEngine, InsightEngine
from talentcopilot.intelligence_core.models import (
    DecisionEffort,
    DecisionPriority,
    DecisionStatus,
)
from talentcopilot.ui.decision_queue import decisions_dataframe


def _insight(severity="High", confidence=0.9, priority="Immediate"):
    return InsightEngine().build(
        insight_id="knowledge-payroll",
        title="Payroll knowledge concentration",
        category="Knowledge",
        severity=severity,
        confidence=confidence,
        current_situation="One employee holds the critical payroll knowledge.",
        business_impact="Payroll continuity is exposed.",
        evidence=[
            {"label": "Experts", "detail": "1", "strength": 1.0},
            {"label": "Backups", "detail": "0", "strength": 0.9},
        ],
        recommendations=[
            {
                "action": "Train two payroll backups",
                "priority": priority,
                "timeframe": "30 days",
                "business_value": "Protect payroll continuity",
            }
        ],
    )


def test_decision_engine_builds_prioritized_decision():
    queue = DecisionEngine().generate([_insight()])
    assert len(queue.decisions) == 1
    decision = queue.decisions[0]
    assert decision.priority == DecisionPriority.DO_NOW
    assert decision.status == DecisionStatus.PROPOSED
    assert decision.effort == DecisionEffort.MEDIUM
    assert decision.confidence_percent == 90
    assert decision.source_insight_id == "knowledge-payroll"
    assert queue.do_now_count == 1


def test_decision_engine_deduplicates_actions():
    insight = _insight()
    queue = DecisionEngine().generate([insight, insight])
    assert len(queue.decisions) == 1


def test_decision_queue_export_contract():
    queue = DecisionEngine().generate([_insight()])
    frame = decisions_dataframe(queue)
    assert not frame.empty
    assert set(["priority", "decision", "status", "effort", "horizon"]).issubset(frame.columns)


def test_empty_decision_queue_is_supported():
    queue = DecisionEngine().generate([])
    assert queue.decisions == ()
    assert queue.do_now_count == 0
