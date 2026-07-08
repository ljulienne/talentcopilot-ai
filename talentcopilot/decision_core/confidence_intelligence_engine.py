from talentcopilot.decision_core.budget_intelligence_models import BudgetIntelligenceReport
from talentcopilot.decision_core.confidence_intelligence_models import (
    ConfidenceDriver,
    ConfidenceGap,
    ConfidenceIntelligenceReport,
)
from talentcopilot.decision_core.evidence_intelligence_models import EvidenceIntelligenceReport
from talentcopilot.decision_core.fit_intelligence_models import FitIntelligenceReport
from talentcopilot.decision_core.models import DecisionTrace, DecisionTraceStep, EvidenceGraph
from talentcopilot.decision_core.risk_intelligence_models import RiskIntelligenceReport


class ConfidenceIntelligenceEngine:
    def evaluate(
        self,
        graph: EvidenceGraph,
        evidence_report: EvidenceIntelligenceReport,
        fit_report: FitIntelligenceReport,
        risk_report: RiskIntelligenceReport,
        trace: DecisionTrace,
        budget_report: BudgetIntelligenceReport | None = None,
    ) -> ConfidenceIntelligenceReport:
        drivers = []
        gaps = []

        evidence_component = evidence_report.evidence_readiness_score
        trace_component = self._trace_completeness(trace)
        risk_component = max(0, 100 - risk_report.risk_score)

        if evidence_component >= 80:
            drivers.append(ConfidenceDriver("Evidence", "Evidence readiness is strong.", 25))
        elif evidence_component < 50:
            gaps.append(
                ConfidenceGap(
                    "Evidence",
                    "High",
                    "Evidence readiness is weak.",
                    "Collect more evidence before final decision.",
                )
            )

        if trace_component >= 80:
            drivers.append(ConfidenceDriver("Traceability", "Decision Trace is sufficiently complete.", 20))
        else:
            gaps.append(
                ConfidenceGap(
                    "Traceability",
                    "Medium",
                    "Decision Trace has limited steps.",
                    "Run all required Decision Core engines.",
                )
            )

        if risk_report.risk_level in {"Low", "Medium"}:
            drivers.append(ConfidenceDriver("Risk", f"Risk level is {risk_report.risk_level}.", 15))
        else:
            gaps.append(
                ConfidenceGap(
                    "Risk",
                    "Medium",
                    f"Risk level is {risk_report.risk_level}.",
                    "Resolve or mitigate key risk factors.",
                )
            )

        budget_component = 75
        if budget_report:
            budget_component = budget_report.budget_fit_score
            drivers.append(
                ConfidenceDriver(
                    "Budget",
                    "Budget signal is available.",
                    10,
                )
            )
        else:
            gaps.append(
                ConfidenceGap(
                    "Budget",
                    "Low",
                    "Budget signal is not available.",
                    "Add budget context to improve decision confidence.",
                )
            )

        fit_stability_component = 80
        if fit_report.gaps and fit_report.fit_score >= 80:
            fit_stability_component = 65
            gaps.append(
                ConfidenceGap(
                    "Fit stability",
                    "Medium",
                    "High fit score still has unresolved fit gaps.",
                    "Validate gaps in interview.",
                )
            )
        elif fit_report.fit_score < 30 and not fit_report.gaps:
            fit_stability_component = 60

        confidence = int(
            evidence_component * 0.35
            + trace_component * 0.20
            + risk_component * 0.20
            + budget_component * 0.10
            + fit_stability_component * 0.15
        )
        confidence = max(0, min(100, confidence))

        level = self._level(confidence)
        decision_quality = self._decision_quality(confidence, risk_report.risk_score)
        summary = (
            f"Confidence score is {confidence}%. "
            f"Evidence={evidence_component}%, Trace={trace_component}%, Risk confidence={risk_component}%."
        )

        return ConfidenceIntelligenceReport(
            candidate_name=graph.candidate_name,
            confidence_score=confidence,
            confidence_level=level,
            decision_quality=decision_quality,
            drivers=drivers,
            gaps=gaps,
            summary=summary,
        )

    def add_trace_step(self, trace, graph: EvidenceGraph, report: ConfidenceIntelligenceReport):
        trace.add_step(
            DecisionTraceStep(
                step_id=f"confidence_intelligence_{graph.graph_id}",
                engine="ConfidenceIntelligenceEngine",
                action="EVALUATE_ANALYSIS_CONFIDENCE",
                input_refs=[graph.graph_id],
                output_ref=str(report.confidence_score),
                explanation=report.summary,
            )
        )
        return trace

    def _trace_completeness(self, trace: DecisionTrace) -> int:
        required = {
            "CREATE_EVIDENCE_GRAPH",
            "EVALUATE_EVIDENCE_QUALITY",
            "EVALUATE_CANDIDATE_FIT",
            "EVALUATE_HIRING_RISK",
        }
        present = {step.action for step in trace.steps}
        return int((len(required.intersection(present)) / len(required)) * 100)

    def _level(self, score: int) -> str:
        if score >= 85:
            return "High"
        if score >= 65:
            return "Medium"
        if score >= 45:
            return "Low"
        return "Very Low"

    def _decision_quality(self, confidence: int, risk_score: int) -> str:
        if confidence >= 85 and risk_score < 35:
            return "Decision-ready"
        if confidence >= 65:
            return "Decision possible with review"
        if confidence >= 45:
            return "Needs more validation"
        return "Not decision-ready"
