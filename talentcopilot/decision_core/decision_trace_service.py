from hashlib import md5

from talentcopilot.decision_core.models import DecisionTrace, DecisionTraceStep, EvidenceGraph


class DecisionTraceService:
    def initialize_trace(self, candidate_name: str, graph: EvidenceGraph) -> DecisionTrace:
        trace = DecisionTrace(
            trace_id=self._id("trace", candidate_name, graph.graph_id),
            candidate_name=candidate_name,
            steps=[],
        )

        trace.add_step(
            DecisionTraceStep(
                step_id=self._id("step", candidate_name, "evidence_graph_created"),
                engine="EvidenceGraphBuilder",
                action="CREATE_EVIDENCE_GRAPH",
                input_refs=[source.source_id for source in graph.sources],
                output_ref=graph.graph_id,
                explanation="Candidate profile was converted into an Evidence Graph.",
            )
        )

        trace.add_step(
            DecisionTraceStep(
                step_id=self._id("step", candidate_name, "coverage_calculated"),
                engine="EvidenceIntelligence",
                action="CALCULATE_EVIDENCE_COVERAGE",
                input_refs=[node.node_id for node in graph.nodes],
                output_ref=str(graph.evidence_coverage()),
                explanation="Evidence coverage is the share of nodes linked to a source.",
            )
        )

        return trace

    def _id(self, *parts: str) -> str:
        raw = "::".join(parts)
        return md5(raw.encode("utf-8")).hexdigest()[:16]
