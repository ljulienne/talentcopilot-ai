from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Mapping

from talentcopilot.interview.pro_models import (
    HiringRecommendation,
    InterviewEvidenceRating,
    InterviewOutcome,
    StarAssessment,
)


class InterviewIntelligenceProService:
    """Evidence-led post-interview intelligence.

    Blueprint guardrails:
    - never mutates or recalculates official fit, rank, or AI confidence;
    - evaluates only recruiter-provided interview evidence;
    - recommendations remain explainable and reversible.
    """

    ENGINE_VERSION = "4.7.1"

    _SITUATION_MARKERS = (
        # English
        "when ", "during ", "in my previous", "at ", "the context", "the situation",
        "we faced", "the project", "the programme", "the program",
        # French (text is accent-normalised before matching)
        "lorsque ", "quand ", "pendant ", "durant ", "lors d'", "dans le cadre", "dans mon precedent",
        "dans mon ancienne", "au sein de", "chez ", "le contexte", "la situation",
        "nous avons rencontre", "nous faisions face", "le projet", "le programme",
    )
    _TASK_MARKERS = (
        # English
        "my responsibility", "i was responsible", "my objective", "my task",
        "i needed to", "i had to", "the goal", "i owned",
        # French
        "ma responsabilite", "j'etais responsable", "mon objectif", "ma mission",
        "ma tache", "je devais", "j'ai du", "il fallait que je", "j'avais pour objectif",
        "j'avais la responsabilite", "j'etais charge", "le but",
    )
    _ACTION_MARKERS = (
        # English
        "i implemented", "i designed", "i led", "i created", "i analysed",
        "i analyzed", "i configured", "i decided", "i changed", "i built",
        "i negotiated", "i facilitated", "i resolved", "i introduced",
        # French
        "j'ai mis en place", "j'ai implemente", "j'ai concu", "j'ai pilote",
        "j'ai dirige", "j'ai mene", "j'ai cree", "j'ai analyse", "j'ai configure",
        "j'ai decide", "j'ai modifie", "j'ai construit", "j'ai negocie",
        "j'ai anime", "j'ai facilite", "j'ai resolu", "j'ai introduit",
        "j'ai deploye", "j'ai coordonne", "j'ai accompagne", "j'ai organise",
    )
    _RESULT_MARKERS = (
        # English
        "result", "outcome", "improved", "reduced", "increased", "delivered",
        "achieved", "saved", "adoption", "completed", "launched", "went live",
        # French
        "resultat", "impact", "ameliore", "reduit", "augmente", "livre",
        "atteint", "economise", "adoption", "termine", "lance", "mis en production",
        "mise en production", "gain", "baisse", "hausse", "a permis", "nous avons obtenu",
    )
    _OWNERSHIP_MARKERS = (
        # English
        " i ", " my ", "personally", "i owned", "i decided", "i led",
        # French
        " je ", " j'", " mon ", " ma ", " mes ", "personnellement",
        "j'ai", "j'etais", "j'avais", "j'ai decide", "j'ai pilote",
    )


    def assess_star(self, answer: str) -> StarAssessment:
        text = " ".join(str(answer or "").strip().split())
        lower = f" {self._normalise(text)} "

        situation = self._contains(lower, self._SITUATION_MARKERS)
        task = self._contains(lower, self._TASK_MARKERS)
        action = self._contains(lower, self._ACTION_MARKERS)
        result = self._contains(lower, self._RESULT_MARKERS)
        ownership = self._contains(lower, self._OWNERSHIP_MARKERS)
        metrics = bool(
            re.search(
                r"\b\d+(?:[.,]\d+)?\s*(?:%|percent|pour\s*cent|jours?|semaines?|"
                r"mois|ans?|annees?|days?|weeks?|months?|years?|heures?|hours?|k|m|"
                r"millions?|euros?|€)?\b",
                lower,
            )
        )

        checks = {
            "Situation / context": situation,
            "Task / responsibility": task,
            "Action taken": action,
            "Result / outcome": result,
            "Personal ownership": ownership,
            "Measurable evidence": metrics,
        }
        missing = [label for label, present in checks.items() if not present]
        score = round(100 * sum(checks.values()) / len(checks))

        if not text:
            summary = "No interview evidence captured."
        elif score >= 84:
            summary = "Complete, evidence-rich STAR answer."
        elif score >= 50:
            summary = "Partially structured answer; targeted follow-up is required."
        else:
            summary = "Insufficiently evidenced answer; ownership and outcomes remain unclear."

        return StarAssessment(
            situation=situation,
            task=task,
            action=action,
            result=result,
            ownership=ownership,
            metrics=metrics,
            completeness_score=score,
            missing_elements=missing,
            evidence_summary=summary,
        )

    def suggest_follow_ups(self, star: StarAssessment, competency: str) -> list[str]:
        prompts = {
            "Situation / context": f"What was the precise context and business risk around {competency}?",
            "Task / responsibility": "What were you personally accountable for?",
            "Action taken": "Which decisions and actions did you personally take?",
            "Result / outcome": "What changed because of your intervention?",
            "Personal ownership": "How did your contribution differ from the wider team's work?",
            "Measurable evidence": "Which KPI, baseline, target, or measurable outcome demonstrates success?",
        }
        return [prompts[item] for item in star.missing_elements if item in prompts]

    def build_rating(
        self,
        competency: str,
        answer: str,
        recruiter_score: int,
        evidence_confirmed: bool,
        notes: str = "",
    ) -> InterviewEvidenceRating:
        score = max(1, min(5, int(recruiter_score)))
        star = self.assess_star(answer)
        return InterviewEvidenceRating(
            competency=str(competency).strip() or "Competency",
            score=score,
            evidence_confirmed=bool(evidence_confirmed),
            notes=str(notes or answer or "").strip(),
            star=star,
        )

    def evaluate(
        self,
        candidate_name: str,
        ratings: Iterable[InterviewEvidenceRating],
    ) -> InterviewOutcome:
        items = list(ratings)
        if not items:
            recommendation = HiringRecommendation(
                label="Needs Evaluation",
                confidence=0,
                rationale=["No interview evidence has been captured."],
                remaining_risks=["All priority competencies remain unvalidated."],
                next_step="Complete the structured interview scorecard.",
            )
            return InterviewOutcome(
                candidate_name=candidate_name,
                overall_score=0.0,
                evidence_coverage=0,
                recommendation=recommendation,
                ratings=[],
            )

        average = sum(item.score for item in items) / len(items)
        confirmed = [item for item in items if item.evidence_confirmed]
        coverage = round(100 * len(confirmed) / len(items))
        star_average = round(sum(item.star.completeness_score for item in items) / len(items))
        weak = [item.competency for item in items if item.score <= 2]
        unconfirmed = [item.competency for item in items if not item.evidence_confirmed]

        if average >= 4.5 and coverage >= 85 and star_average >= 70 and not weak:
            label = "Strong Hire"
            next_step = "Proceed to the final decision with documented evidence."
        elif average >= 3.7 and coverage >= 65 and not weak:
            label = "Hire"
            next_step = "Proceed, while closing any explicitly listed evidence gaps."
        elif average >= 2.8:
            label = "Borderline"
            next_step = "Run a targeted follow-up interview before making a hiring decision."
        else:
            label = "No Hire"
            next_step = "Do not proceed without materially different evidence."

        confidence = round(min(100, (coverage * 0.55) + (star_average * 0.45)))
        rationale = [
            f"Recruiter scorecard average: {average:.2f}/5.",
            f"Confirmed competency evidence: {coverage}%.",
            f"Average STAR completeness: {star_average}%.",
        ]
        remaining = []
        if weak:
            remaining.append("Low ratings: " + ", ".join(weak))
        if unconfirmed:
            remaining.append("Evidence not confirmed: " + ", ".join(unconfirmed))
        for item in items:
            if item.star.missing_elements:
                remaining.append(
                    f"{item.competency}: missing " + ", ".join(item.star.missing_elements)
                )

        return InterviewOutcome(
            candidate_name=candidate_name,
            overall_score=round(average, 2),
            evidence_coverage=coverage,
            recommendation=HiringRecommendation(
                label=label,
                confidence=confidence,
                rationale=rationale,
                remaining_risks=remaining,
                next_step=next_step,
            ),
            ratings=items,
        )

    def build_executive_summary(self, outcome: InterviewOutcome) -> str:
        recommendation = outcome.recommendation
        risks = (
            "; ".join(recommendation.remaining_risks[:3])
            if recommendation.remaining_risks
            else "No material evidence gap remains."
        )
        return (
            f"{outcome.candidate_name} received an interview score of "
            f"{outcome.overall_score:.2f}/5 with {outcome.evidence_coverage}% evidence coverage. "
            f"Recommendation: {recommendation.label} ({recommendation.confidence}% confidence). "
            f"Remaining validation: {risks}"
        )

    @staticmethod
    def _normalise(text: str) -> str:
        value = str(text or "").replace("’", "'").replace("`", "'").casefold()
        return "".join(
            character
            for character in unicodedata.normalize("NFKD", value)
            if not unicodedata.combining(character)
        )

    @staticmethod
    def _contains(text: str, markers: Iterable[str]) -> bool:
        return any(marker in text for marker in markers)
