from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput


class LLMHybridMatchingAdapter:
    def build_report(self, candidate_extraction, role_extraction):
        facts = candidate_extraction.facts
        insights = candidate_extraction.insights
        role = role_extraction.facts

        titles = []
        if facts.current_title:
            titles.append(facts.current_title)
        if facts.headline:
            titles.append(facts.headline)

        achievements = list(facts.achievements or [])
        responsibilities = list(facts.responsibilities or [])

        if insights:
            achievements.extend(insights.leadership_signals or [])
            achievements.extend(insights.transformation_signals or [])
            responsibilities.extend(insights.international_signals or [])

        return HybridMatchingEngine().analyze(
            HybridMatchingInput(
                candidate_name=facts.candidate_name or "Unknown Candidate",
                role_title=role.title or "Unknown Role",
                candidate_skills=list(dict.fromkeys([*(facts.skills or []), *(facts.technologies or [])])),
                required_skills=list(dict.fromkeys([*(role.required_skills or []), *(role.preferred_skills or [])])),
                years_experience=int(facts.years_experience or 0),
                titles=titles,
                achievements=achievements,
                responsibilities=responsibilities,
            )
        )
