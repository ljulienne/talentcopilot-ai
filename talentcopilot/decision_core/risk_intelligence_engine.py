from talentcopilot.decision_core.evidence_intelligence_models import EvidenceIntelligenceReport
from talentcopilot.decision_core.fit_intelligence_models import FitIntelligenceReport, RoleRequirements
from talentcopilot.decision_core.models import DecisionTraceStep, EvidenceGraph
from talentcopilot.decision_core.risk_intelligence_models import RiskFactor, RiskIntelligenceReport


class RiskIntelligenceEngine:
    def evaluate(
        self,
        graph: EvidenceGraph,
        role: RoleRequirements,
        evidence_report: EvidenceIntelligenceReport,
        fit_report: FitIntelligenceReport,
    ) -> RiskIntelligenceReport:
        factors = []

        for gap in fit_report.gaps:
            if gap.severity == "High":
                factors.append(
                    RiskFactor(
                        area=gap.area,
                        severity="High",
                        detail=gap.detail,
                        mitigation="Validate in interview or reject if requirement is mandatory.",
                    )
                )
            else:
                factors.append(
                    RiskFactor(
                        area=gap.area,
                        severity="Medium",
                        detail=gap.detail,
                        mitigation="Clarify with candidate and hiring manager.",
                    )
                )

        for gap in evidence_report.gaps:
            severity = "High" if gap.severity == "High" else "Medium"
            factors.append(
                RiskFactor(
                    area=f"Evidence — {gap.area}",
                    severity=severity,
                    detail=gap.detail,
                    mitigation="Request more evidence or validate through structured interview.",
                )
            )

        if fit_report.fit_score < 30:
            factors.append(
                RiskFactor(
                    area="Candidate fit",
                    severity="High",
                    detail="Candidate fit is very low for the current role.",
                    mitigation="Do not proceed unless role criteria change.",
                )
            )
        elif fit_report.fit_score < 50:
            factors.append(
                RiskFactor(
                    area="Candidate fit",
                    severity="Medium",
                    detail="Candidate fit is weak and requires careful review.",
                    mitigation="Compare with stronger candidates before interview.",
                )
            )

        if evidence_report.evidence_readiness_score < 40:
            factors.append(
                RiskFactor(
                    area="Decision quality",
                    severity="High",
                    detail="Evidence is insufficient for a reliable decision.",
                    mitigation="Do not make a final decision until more evidence is collected.",
                )
            )

        risk_score = self._score(factors)
        risk_level = self._level(risk_score)
        mitigations = []
        for factor in factors:
            if factor.mitigation not in mitigations:
                mitigations.append(factor.mitigation)

        summary = (
            f"Risk level is {risk_level} with a risk score of {risk_score}%. "
            f"{len(factors)} risk factor(s) identified."
        )

        return RiskIntelligenceReport(
            candidate_name=graph.candidate_name,
            role_title=role.role_title,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=factors,
            mitigation_actions=mitigations,
            summary=summary,
        )

    def add_trace_step(self, trace, graph: EvidenceGraph, report: RiskIntelligenceReport):
        trace.add_step(
            DecisionTraceStep(
                step_id=f"risk_intelligence_{graph.graph_id}",
                engine="RiskIntelligenceEngine",
                action="EVALUATE_HIRING_RISK",
                input_refs=[graph.graph_id],
                output_ref=report.risk_level,
                explanation=report.summary,
            )
        )
        return trace

    def _score(self, factors: list[RiskFactor]) -> int:
        score = 0
        for factor in factors:
            if factor.severity == "High":
                score += 30
            elif factor.severity == "Medium":
                score += 15
            else:
                score += 5
        return max(0, min(100, score))

    def _level(self, risk_score: int) -> str:
        if risk_score >= 75:
            return "Critical"
        if risk_score >= 50:
            return "High"
        if risk_score >= 25:
            return "Medium"
        return "Low"
