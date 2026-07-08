from talentcopilot.decision_core.evidence_intelligence_models import (
    EvidenceGap,
    EvidenceIntelligenceReport,
    EvidenceStrength,
)
from talentcopilot.decision_core.models import DecisionTraceStep, EvidenceGraph


class EvidenceIntelligenceEngine:
    REQUIRED_EVIDENCE_TYPES = {
        "candidate": "Candidate identity",
        "skill": "Skills",
        "experience": "Experience",
        "achievement": "Achievements",
    }

    def evaluate(self, graph: EvidenceGraph) -> EvidenceIntelligenceReport:
        node_count = len(graph.nodes)
        edge_count = len(graph.edges)

        coverage = graph.evidence_coverage()
        reliability = self._reliability(graph)
        density = self._density(node_count, edge_count)
        quality = int((coverage * 0.4) + (reliability * 0.4) + (density * 0.2))

        gaps = self._gaps(graph)
        strengths = self._strengths(graph)

        gap_penalty = min(30, len([g for g in gaps if g.severity == "High"]) * 12 + len(gaps) * 3)
        readiness = max(0, min(100, int((quality + coverage + reliability) / 3) - gap_penalty))

        status = self._status(readiness)
        summary = (
            f"Evidence readiness is {readiness}%. "
            f"Coverage={coverage}%, Reliability={reliability}%, Density={density}%."
        )

        return EvidenceIntelligenceReport(
            candidate_name=graph.candidate_name,
            evidence_quality_score=quality,
            evidence_coverage_score=coverage,
            evidence_reliability_score=reliability,
            evidence_density_score=density,
            evidence_readiness_score=readiness,
            status=status,
            strengths=strengths,
            gaps=gaps,
            summary=summary,
        )

    def add_trace_step(self, trace, graph: EvidenceGraph, report: EvidenceIntelligenceReport):
        trace.add_step(
            DecisionTraceStep(
                step_id=f"evidence_intelligence_{graph.graph_id}",
                engine="EvidenceIntelligenceEngine",
                action="EVALUATE_EVIDENCE_QUALITY",
                input_refs=[graph.graph_id],
                output_ref=str(report.evidence_readiness_score),
                explanation=report.summary,
            )
        )
        return trace

    def _reliability(self, graph: EvidenceGraph) -> int:
        if not graph.nodes:
            return 0
        avg_confidence = sum(max(0, min(100, node.confidence)) for node in graph.nodes) / len(graph.nodes)
        sourced_ratio = graph.evidence_coverage()
        return int((avg_confidence * 0.65) + (sourced_ratio * 0.35))

    def _density(self, node_count: int, edge_count: int) -> int:
        if node_count == 0:
            return 0
        ratio = edge_count / max(1, node_count - 1)
        return int(max(0, min(100, ratio * 100)))

    def _gaps(self, graph: EvidenceGraph) -> list[EvidenceGap]:
        present = {node.node_type for node in graph.nodes}
        gaps = []

        for node_type, label in self.REQUIRED_EVIDENCE_TYPES.items():
            if node_type not in present:
                severity = "High" if node_type in {"candidate", "experience"} else "Medium"
                gaps.append(
                    EvidenceGap(
                        area=label,
                        severity=severity,
                        detail=f"No evidence node found for {label.lower()}.",
                    )
                )

        unsourced = [node for node in graph.nodes if not node.source_ids]
        if unsourced:
            gaps.append(
                EvidenceGap(
                    area="Traceability",
                    severity="High",
                    detail=f"{len(unsourced)} evidence node(s) have no source reference.",
                )
            )

        low_confidence = [node for node in graph.nodes if node.confidence < 50]
        if low_confidence:
            gaps.append(
                EvidenceGap(
                    area="Reliability",
                    severity="Medium",
                    detail=f"{len(low_confidence)} evidence node(s) have low confidence.",
                )
            )

        return gaps

    def _strengths(self, graph: EvidenceGraph) -> list[EvidenceStrength]:
        strengths = []

        for node_type, label in self.REQUIRED_EVIDENCE_TYPES.items():
            nodes = graph.find_nodes_by_type(node_type)
            if nodes:
                avg = int(sum(node.confidence for node in nodes) / len(nodes))
                strengths.append(
                    EvidenceStrength(
                        area=label,
                        detail=f"{len(nodes)} evidence node(s) available.",
                        confidence=avg,
                    )
                )

        if graph.evidence_coverage() == 100 and graph.nodes:
            strengths.append(
                EvidenceStrength(
                    area="Traceability",
                    detail="All evidence nodes are linked to sources.",
                    confidence=100,
                )
            )

        return strengths

    def _status(self, readiness: int) -> str:
        if readiness >= 85:
            return "Strong evidence"
        if readiness >= 65:
            return "Usable evidence"
        if readiness >= 40:
            return "Limited evidence"
        return "Insufficient evidence"
