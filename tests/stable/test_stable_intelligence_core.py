from talentcopilot.intelligence_core.adapters import KnowledgeInsightAdapter
from talentcopilot.intelligence_core.engine import ExecutiveEngine, InsightEngine
from talentcopilot.intelligence_core.models import DecisionReadiness, Severity
from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees
from talentcopilot.organization_intelligence.knowledge_engine import KnowledgeConcentrationEngine


def test_insight_engine_builds_explainable_contract():
    insight = InsightEngine().build(
        insight_id="knowledge-payroll",
        title="Payroll dependency",
        category="Knowledge",
        severity="High",
        confidence=0.9,
        current_situation="One expert holds payroll knowledge.",
        business_impact="Payroll continuity is exposed.",
        evidence=[
            {"label": "Experts", "detail": "1", "strength": 1.0},
            {"label": "Backups", "detail": "0", "strength": 0.9},
        ],
        recommendations=[
            {"action": "Train a backup", "priority": "Immediate", "timeframe": "90 days", "business_value": "Continuity"}
        ],
    )
    assert insight.severity == Severity.HIGH
    assert insight.decision_readiness == DecisionReadiness.READY
    assert insight.confidence_percent == 90
    assert insight.evidence_quality in {"Good", "Excellent"}


def test_knowledge_adapter_and_executive_engine():
    employees = dataframe_to_employees(demo_dataframe())
    diagnostic = KnowledgeConcentrationEngine().analyze(employees)
    insights = KnowledgeInsightAdapter().from_diagnostic(diagnostic)
    brief = ExecutiveEngine().generate(insights)
    assert insights
    assert brief.priority_insights
    assert brief.recommended_decisions
    assert brief.confidence > 0
    assert brief.overall_severity in {Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW}


def test_executive_engine_handles_empty_input():
    brief = ExecutiveEngine().generate([])
    assert brief.decision_readiness == DecisionReadiness.NOT_READY
    assert brief.priority_insights == ()
