from collections import Counter

from talentcopilot.models.talent_intelligence import (
    TalentIntelligenceReport,
    TalentRecommendation,
    TalentShortlistLine,
    TalentSignal,
)


class TalentIntelligenceService:
    def build(self, session=None) -> TalentIntelligenceReport:
        if session is None or not getattr(session, "ranked_analyses", None):
            return self._empty_report()

        candidates_by_name = {}
        all_skills = []

        for candidate in getattr(session, "candidates", []) or []:
            name = candidate.get("name")
            if name:
                candidates_by_name[name] = candidate
            all_skills.extend([str(skill) for skill in candidate.get("skills", [])])

        shortlist = []
        for analysis in session.ranked_analyses[:8]:
            candidate = candidates_by_name.get(analysis.candidate_name, {})
            top_skills = [str(skill) for skill in candidate.get("skills", [])[:4]]
            shortlist.append(
                TalentShortlistLine(
                    candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                    rank=int(getattr(analysis, "rank", 0) or 0),
                    match_score=float(getattr(analysis, "match_score", 0) or 0),
                    top_skills=top_skills,
                    sourcing_note="Strong internal candidate signal." if getattr(analysis, "match_score", 0) >= 75 else "Requires additional validation.",
                )
            )

        skill_counter = Counter(all_skills)
        total_candidates = max(1, len(getattr(session, "candidates", []) or []))
        skill_signals = [
            TalentSignal(
                name=skill,
                coverage=int((count / total_candidates) * 100),
                evidence_count=count,
            )
            for skill, count in skill_counter.most_common(8)
        ]

        readiness = min(96, 60 + len(shortlist) * 5 + min(20, len(skill_signals) * 2))

        return TalentIntelligenceReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            search_readiness=readiness,
            shortlist=shortlist,
            skill_signals=skill_signals,
            recommendations=[
                TalentRecommendation("Review internal shortlist", "Start with the top-ranked internal profiles.", "High"),
                TalentRecommendation("Validate scarce skills", "Check whether critical requirements are covered by enough candidates.", "High"),
                TalentRecommendation("Prepare external sourcing", "If internal coverage is weak, define external sourcing criteria.", "Medium"),
            ],
        )

    def _empty_report(self) -> TalentIntelligenceReport:
        return TalentIntelligenceReport(
            role_title="No active recruitment",
            session_id="-",
            search_readiness=0,
            shortlist=[],
            skill_signals=[],
            recommendations=[
                TalentRecommendation("Load Enterprise Demo", "Start a recruitment session to activate Talent Intelligence.", "High")
            ],
        )
