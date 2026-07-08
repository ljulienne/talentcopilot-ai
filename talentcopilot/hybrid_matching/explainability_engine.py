from talentcopilot.hybrid_matching.explainability_models import (
    HybridExplanationReport,
    HybridScoreBreakdown,
    ScoreContribution,
)


class HybridExplainabilityEngine:
    def explain(self, report) -> HybridExplanationReport:
        positives = []
        penalties = []
        focus_areas = []

        semantic_points = int(report.semantic_score * 0.5)
        career_points = int(report.career_score * 0.3)
        evidence_points = 0
        penalty_points = 0

        positives.append(
            ScoreContribution(
                category="Semantic Skills",
                label="Skill proximity",
                points=semantic_points,
                evidence=[
                    f"{m.required_skill} matched with {m.candidate_skill or 'no match'} ({m.score}%)"
                    for m in report.semantic_skill_report.matches
                    if m.score >= 70
                ][:6],
                explanation="Candidate skills are compared against role requirements using semantic proximity.",
            )
        )

        missing = report.semantic_skill_report.missing_skills
        if missing:
            penalty = min(25, len(missing) * 8)
            penalty_points += penalty
            focus_areas.extend(missing)
            penalties.append(
                ScoreContribution(
                    category="Skill Gaps",
                    label="Missing or weak required skills",
                    points=-penalty,
                    evidence=missing,
                    explanation="Some required skills were not sufficiently covered by semantic matching.",
                )
            )

        if report.career_report:
            career_evidence = []
            for signal in report.career_report.signals:
                if signal.score >= 60:
                    career_evidence.append(f"{signal.category}: {signal.label} ({signal.score}%)")
                    evidence_points += 2

            positives.append(
                ScoreContribution(
                    category="Career",
                    label=f"Career maturity: {report.career_report.seniority_level}",
                    points=career_points,
                    evidence=career_evidence[:6],
                    explanation="Career score reflects seniority, progression and achievement signals.",
                )
            )

            if report.career_report.impact_score >= 60:
                positives.append(
                    ScoreContribution(
                        category="Evidence",
                        label="Business impact evidence",
                        points=10,
                        evidence=[
                            ev
                            for signal in report.career_report.signals
                            if signal.category == "Impact"
                            for ev in signal.evidence
                        ][:5],
                        explanation="Quantified achievements increase confidence in real-world impact.",
                    )
                )
                evidence_points += 10

            if report.career_report.career_score < 45:
                penalty_points += 10
                penalties.append(
                    ScoreContribution(
                        category="Career",
                        label="Limited career evidence",
                        points=-10,
                        evidence=[],
                        explanation="Career signals are limited or insufficiently supported.",
                    )
                )

        final_score = max(0, min(100, semantic_points + career_points + evidence_points - penalty_points))

        summary = self._summary(report, final_score, positives, penalties)

        return HybridExplanationReport(
            candidate_name=report.candidate_name,
            role_title=report.role_title,
            breakdown=HybridScoreBreakdown(
                semantic_points=semantic_points,
                career_points=career_points,
                evidence_points=evidence_points,
                penalties=penalty_points,
                final_score=final_score,
            ),
            positive_contributions=positives,
            penalties=penalties,
            recruiter_summary=summary,
            focus_areas=focus_areas,
        )

    def _summary(self, report, score, positives, penalties) -> str:
        if score >= 80:
            verdict = "strong semantic and career alignment"
        elif score >= 65:
            verdict = "good alignment with some validation points"
        elif score >= 50:
            verdict = "partial alignment requiring further evidence"
        else:
            verdict = "limited alignment based on available evidence"

        return (
            f"{report.candidate_name} shows {verdict} for {report.role_title}. "
            f"The score is driven by semantic skill proximity and career evidence, "
            f"with {len(penalties)} notable penalty area(s)."
        )
