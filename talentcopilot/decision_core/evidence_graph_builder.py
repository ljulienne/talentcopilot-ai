from hashlib import md5

from talentcopilot.decision_core.models import (
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    EvidenceSource,
)


class EvidenceGraphBuilder:
    def build_from_candidate_dict(self, candidate: dict, role_title: str = "Recruitment") -> EvidenceGraph:
        name = candidate.get("name", "Candidate")
        graph_id = self._id("graph", name, role_title)

        source = EvidenceSource(
            source_id=self._id("source", name, "profile"),
            source_type="candidate_profile",
            label=f"{name} profile",
            excerpt=str(candidate),
        )

        graph = EvidenceGraph(
            graph_id=graph_id,
            candidate_name=name,
            sources=[source],
            nodes=[],
            edges=[],
        )

        candidate_node = EvidenceNode(
            node_id=self._id("node", name, "identity"),
            node_type="candidate",
            label=name,
            confidence=100,
            source_ids=[source.source_id],
        )
        graph.nodes.append(candidate_node)

        for skill in candidate.get("skills", []) or []:
            skill_node = EvidenceNode(
                node_id=self._id("skill", name, str(skill)),
                node_type="skill",
                label=str(skill),
                confidence=85,
                source_ids=[source.source_id],
            )
            graph.nodes.append(skill_node)
            graph.edges.append(
                EvidenceEdge(candidate_node.node_id, "HAS_SKILL", skill_node.node_id, 85)
            )

        for achievement in candidate.get("achievements", []) or []:
            achievement_node = EvidenceNode(
                node_id=self._id("achievement", name, str(achievement)),
                node_type="achievement",
                label=str(achievement),
                confidence=82,
                source_ids=[source.source_id],
            )
            graph.nodes.append(achievement_node)
            graph.edges.append(
                EvidenceEdge(candidate_node.node_id, "HAS_ACHIEVEMENT", achievement_node.node_id, 82)
            )

        years = candidate.get("years_experience")
        if years is not None:
            experience_node = EvidenceNode(
                node_id=self._id("experience", name, str(years)),
                node_type="experience",
                label=f"{years} years experience",
                confidence=90,
                source_ids=[source.source_id],
                metadata={"years": str(years)},
            )
            graph.nodes.append(experience_node)
            graph.edges.append(
                EvidenceEdge(candidate_node.node_id, "HAS_EXPERIENCE", experience_node.node_id, 90)
            )

        return graph

    def _id(self, *parts: str) -> str:
        raw = "::".join(parts)
        return md5(raw.encode("utf-8")).hexdigest()[:16]
