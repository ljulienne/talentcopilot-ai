from hashlib import md5

from talentcopilot.decision_core.decision_trace_service import DecisionTraceService
from talentcopilot.decision_core.evidence_graph_builder import EvidenceGraphBuilder
from talentcopilot.decision_core.models import CandidateDecisionProfile


class CandidateDecisionProfileService:
    def build_from_candidate_dict(self, candidate: dict, role_title: str = "Recruitment") -> CandidateDecisionProfile:
        name = candidate.get("name", "Candidate")
        graph = EvidenceGraphBuilder().build_from_candidate_dict(candidate, role_title)
        trace = DecisionTraceService().initialize_trace(name, graph)

        profile = CandidateDecisionProfile(
            profile_id=self._id("profile", name, role_title),
            candidate_name=name,
            role_title=role_title,
            evidence_graph=graph,
            decision_trace=trace,
            metadata={"profile_version": "dic-v2.0-alpha-a"},
        )

        return profile

    def build_many(self, candidates: list[dict], role_title: str = "Recruitment") -> list[CandidateDecisionProfile]:
        return [self.build_from_candidate_dict(candidate, role_title) for candidate in candidates]

    def _id(self, *parts: str) -> str:
        raw = "::".join(parts)
        return md5(raw.encode("utf-8")).hexdigest()[:16]
