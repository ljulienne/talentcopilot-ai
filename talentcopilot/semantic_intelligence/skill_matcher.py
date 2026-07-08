from talentcopilot.semantic_intelligence.models import SemanticSkillReport, SkillMatch
from talentcopilot.semantic_intelligence.skill_graph import SkillGraph


class SemanticSkillMatcher:
    def __init__(self, graph: SkillGraph | None = None):
        self.graph = graph or SkillGraph()

    def compare(self, required_skills: list[str], candidate_skills: list[str]) -> SemanticSkillReport:
        normalized_required = list(dict.fromkeys([self.graph.normalize(skill) for skill in required_skills if skill]))
        normalized_candidate = list(dict.fromkeys([self.graph.normalize(skill) for skill in candidate_skills if skill]))

        matches = []
        for required in normalized_required:
            matches.append(self._best_match(required, normalized_candidate))

        return SemanticSkillReport(
            required_skills=normalized_required,
            candidate_skills=normalized_candidate,
            matches=matches,
        )

    def _best_match(self, required: str, candidates: list[str]) -> SkillMatch:
        if not candidates:
            return SkillMatch(required, None, 0, "missing", f"No candidate skill found for {required}.")

        if required in candidates:
            return SkillMatch(required, required, 100, "exact", f"{required} is explicitly present.")

        required_concept = self.graph.get(required)
        best = SkillMatch(required, None, 0, "missing", f"No semantic match found for {required}.")

        for candidate in candidates:
            candidate_concept = self.graph.get(candidate)
            if not required_concept or not candidate_concept:
                continue

            if required_concept.parent == candidate_concept.canonical or candidate_concept.parent == required_concept.canonical:
                score = 88
                match_type = "parent-child"
                explanation = f"{candidate} is directly connected to {required} in the skill graph."
            elif candidate_concept.canonical in required_concept.related or required_concept.canonical in candidate_concept.related:
                score = 82
                match_type = "related"
                explanation = f"{candidate} is related to {required}."
            elif required_concept.family == candidate_concept.family:
                score = 72
                match_type = "same-family"
                explanation = f"{candidate} and {required} belong to the same family: {required_concept.family}."
            else:
                score = 0
                match_type = "missing"
                explanation = f"{candidate} is not close enough to {required}."

            if score > best.score:
                best = SkillMatch(required, candidate, score, match_type, explanation)

        return best
