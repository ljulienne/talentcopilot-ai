from talentcopilot.decision_core.budget_intelligence_engine import BudgetIntelligenceEngine
from talentcopilot.decision_core.budget_intelligence_models import BudgetContext, CandidateCompensation
from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder
from talentcopilot.decision_core.fit_intelligence_models import FitIntelligenceReport


def test_budget_intelligence_feasible_candidate():
    graph = EvidenceGraphBuilder().build_from_candidate_dict({"name": "Alice Martin"}, "Transformation Lead")
    fit = FitIntelligenceReport("Alice Martin", "Transformation Lead", 85, 85, 80, 70, "Good fit")
    report = BudgetIntelligenceEngine().evaluate(
        graph,
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=90000),
        fit,
    )

    assert report.budget_fit_score >= 75
    assert report.feasibility in {"High", "Medium"}
    assert report.budget_recommendation in {"Budget Feasible", "Budget Review"}


def test_budget_intelligence_strong_candidate_over_budget():
    graph = EvidenceGraphBuilder().build_from_candidate_dict({"name": "Alice Martin"}, "Transformation Lead")
    fit = FitIntelligenceReport("Alice Martin", "Transformation Lead", 92, 90, 90, 80, "Strong fit")
    report = BudgetIntelligenceEngine().evaluate(
        graph,
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=125000),
        fit,
    )

    assert report.budget_fit_score < 60
    assert report.budget_recommendation == "Review Compensation Feasibility"
    assert report.salary_gap > 0
    assert report.mitigation_actions


def test_budget_intelligence_low_fit_budget_not_decisive():
    graph = EvidenceGraphBuilder().build_from_candidate_dict({"name": "David Smith"}, "Transformation Lead")
    fit = FitIntelligenceReport("David Smith", "Transformation Lead", 0, 0, 0, 0, "No fit")
    report = BudgetIntelligenceEngine().evaluate(
        graph,
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=50000),
        fit,
    )

    assert report.budget_recommendation == "Budget Not Decisive"


def test_budget_intelligence_adds_trace_step():
    from talentcopilot.decision_core.decision_trace_service import DecisionTraceService

    graph = EvidenceGraphBuilder().build_from_candidate_dict({"name": "Alice Martin"}, "Transformation Lead")
    fit = FitIntelligenceReport("Alice Martin", "Transformation Lead", 92, 90, 90, 80, "Strong fit")
    report = BudgetIntelligenceEngine().evaluate(
        graph,
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=120000),
        fit,
    )
    trace = DecisionTraceService().initialize_trace("Alice Martin", graph)
    BudgetIntelligenceEngine().add_trace_step(trace, graph, report)

    assert "EVALUATE_BUDGET_FEASIBILITY" in [step.action for step in trace.steps]
