from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EvidenceSource:
    source_id: str
    source_type: str
    label: str
    excerpt: str = ""


@dataclass
class EvidenceNode:
    node_id: str
    node_type: str
    label: str
    confidence: int = 80
    source_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class EvidenceEdge:
    source_node_id: str
    relationship: str
    target_node_id: str
    confidence: int = 80


@dataclass
class EvidenceGraph:
    graph_id: str
    candidate_name: str
    sources: List[EvidenceSource] = field(default_factory=list)
    nodes: List[EvidenceNode] = field(default_factory=list)
    edges: List[EvidenceEdge] = field(default_factory=list)

    def find_nodes_by_type(self, node_type: str) -> List[EvidenceNode]:
        return [node for node in self.nodes if node.node_type == node_type]

    def evidence_coverage(self) -> int:
        if not self.nodes:
            return 0
        traced = len([node for node in self.nodes if node.source_ids])
        return int((traced / len(self.nodes)) * 100)


@dataclass
class DecisionTraceStep:
    step_id: str
    engine: str
    action: str
    input_refs: List[str] = field(default_factory=list)
    output_ref: Optional[str] = None
    explanation: str = ""


@dataclass
class DecisionTrace:
    trace_id: str
    candidate_name: str
    steps: List[DecisionTraceStep] = field(default_factory=list)

    def add_step(self, step: DecisionTraceStep) -> None:
        self.steps.append(step)


@dataclass
class CandidateDecisionProfile:
    profile_id: str
    candidate_name: str
    role_title: str
    evidence_graph: EvidenceGraph
    decision_trace: DecisionTrace
    fit_score: Optional[float] = None
    confidence_score: Optional[int] = None
    recommendation: Optional[str] = None
    risk_level: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def is_ready_for_decision_core(self) -> bool:
        return bool(self.evidence_graph.nodes and self.decision_trace.steps)
