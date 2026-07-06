from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ReasoningInsight:
    title: str
    explanation: str
    evidence: List[str] = field(default_factory=list)
    confidence: str = "medium"


@dataclass
class CandidateReasoningReport:
    candidate_name: str
    role_title: str
    executive_summary: str
    strengths: List[ReasoningInsight]
    risks: List[ReasoningInsight]
    transferable_skills: List[ReasoningInsight]
    uncertainties: List[ReasoningInsight]
    recommendation: str
    recommendation_rationale: str
    challenge: str


class ReasoningEngine:
    """
    Generic evidence-first reasoning engine.

    This engine does not decide for the recruiter.
    It explains what the available evidence suggests,
    highlights uncertainty, and supports human decision-making.
    """

    def build_report(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        match_result: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
    ) -> CandidateReasoningReport:
        candidate_name = candidate.get("name", "Unknown candidate")
        role_title = job.get("title", "Target role")

        evidence = evidence or []
        match_result = match_result or {}

        strengths = self._build_strengths(candidate, job, evidence)
        risks = self._build_risks(candidate, job, evidence)
        transferable_skills = self._build_transferable_skills(candidate, job, evidence)
        uncertainties = self._build_uncertainties(candidate, job, evidence)

        executive_summary = self._build_executive_summary(
            candidate_name=candidate_name,
            role_title=role_title,
            strengths=strengths,
            risks=risks,
            uncertainties=uncertainties,
            match_result=match_result,
        )

        recommendation, rationale = self._build_recommendation(
            strengths=strengths,
            risks=risks,
            uncertainties=uncertainties,
            match_result=match_result,
        )

        challenge = self._build_challenge(
            recommendation=recommendation,
            risks=risks,
            uncertainties=uncertainties,
        )

        return CandidateReasoningReport(
            candidate_name=candidate_name,
            role_title=role_title,
            executive_summary=executive_summary,
            strengths=strengths,
            risks=risks,
            transferable_skills=transferable_skills,
            uncertainties=uncertainties,
            recommendation=recommendation,
            recommendation_rationale=rationale,
            challenge=challenge,
        )

    def _build_strengths(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> List[ReasoningInsight]:
        insights = []

        candidate_skills = set(candidate.get("skills", []))
        required_skills = set(job.get("required_skills", []))

        matched_skills = sorted(candidate_skills.intersection(required_skills))

        if matched_skills:
            insights.append(
                ReasoningInsight(
                    title="Strong alignment with required skills",
                    explanation=(
                        "The candidate shows direct alignment with several skills "
                        "explicitly required for the role."
                    ),
                    evidence=matched_skills,
                    confidence="high",
                )
            )

        for item in evidence[:3]:
            text = item.get("text") or item.get("evidence") or ""
            if text:
                insights.append(
                    ReasoningInsight(
                        title="Relevant documented evidence",
                        explanation=(
                            "The candidate profile contains concrete evidence that may support "
                            "their fit for the target role."
                        ),
                        evidence=[text],
                        confidence=item.get("confidence", "medium"),
                    )
                )

        if not insights:
            insights.append(
                ReasoningInsight(
                    title="Limited explicit strengths detected",
                    explanation=(
                        "The available candidate data does not provide enough explicit evidence "
                        "to identify strong role alignment."
                    ),
                    evidence=[],
                    confidence="low",
                )
            )

        return insights

    def _build_risks(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> List[ReasoningInsight]:
        risks = []

        candidate_skills = set(candidate.get("skills", []))
        required_skills = set(job.get("required_skills", []))

        missing_skills = sorted(required_skills.difference(candidate_skills))

        if missing_skills:
            risks.append(
                ReasoningInsight(
                    title="Potential gaps against required skills",
                    explanation=(
                        "Some required skills are not clearly visible in the candidate profile. "
                        "This does not necessarily mean the candidate lacks them, but they are not "
                        "currently supported by explicit evidence."
                    ),
                    evidence=missing_skills,
                    confidence="medium",
                )
            )

        candidate_experience = candidate.get("years_experience")
        required_experience = job.get("years_experience")

        if (
            isinstance(candidate_experience, (int, float))
            and isinstance(required_experience, (int, float))
            and candidate_experience < required_experience
        ):
            risks.append(
                ReasoningInsight(
                    title="Experience level may be below expectation",
                    explanation=(
                        "The candidate appears to have fewer years of experience than requested "
                        "for the role."
                    ),
                    evidence=[
                        f"Candidate: {candidate_experience} years",
                        f"Required: {required_experience} years",
                    ],
                    confidence="high",
                )
            )

        if not risks:
            risks.append(
                ReasoningInsight(
                    title="No major risk detected from available data",
                    explanation=(
                        "No significant risk is immediately visible based on the structured data "
                        "currently available. This should still be validated during the interview."
                    ),
                    evidence=[],
                    confidence="medium",
                )
            )

        return risks

    def _build_transferable_skills(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> List[ReasoningInsight]:
        transferable = []

        candidate_skills = set(candidate.get("skills", []))
        preferred_skills = set(job.get("preferred_skills", []))

        matched_preferred = sorted(candidate_skills.intersection(preferred_skills))

        if matched_preferred:
            transferable.append(
                ReasoningInsight(
                    title="Additional relevant capabilities",
                    explanation=(
                        "The candidate has additional skills that may not be mandatory but could "
                        "increase their potential contribution in the role."
                    ),
                    evidence=matched_preferred,
                    confidence="medium",
                )
            )

        if not transferable:
            transferable.append(
                ReasoningInsight(
                    title="Transferable skills require validation",
                    explanation=(
                        "The current profile does not provide enough information to identify "
                        "clear transferable skills beyond the explicit matching criteria."
                    ),
                    evidence=[],
                    confidence="low",
                )
            )

        return transferable

    def _build_uncertainties(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> List[ReasoningInsight]:
        uncertainties = []

        if not evidence:
            uncertainties.append(
                ReasoningInsight(
                    title="Limited evidence base",
                    explanation=(
                        "The analysis is based mostly on structured candidate information rather "
                        "than detailed CV evidence. The recruiter should validate key assumptions."
                    ),
                    evidence=[],
                    confidence="high",
                )
            )

        if not candidate.get("achievements"):
            uncertainties.append(
                ReasoningInsight(
                    title="Impact not sufficiently quantified",
                    explanation=(
                        "The candidate profile does not clearly quantify business impact, outcomes, "
                        "or measurable achievements."
                    ),
                    evidence=[],
                    confidence="medium",
                )
            )

        if not uncertainties:
            uncertainties.append(
                ReasoningInsight(
                    title="Remaining uncertainty should be tested in interview",
                    explanation=(
                        "The available evidence is reasonably complete, but interview validation "
                        "is still needed before making a hiring decision."
                    ),
                    evidence=[],
                    confidence="medium",
                )
            )

        return uncertainties

    def _build_executive_summary(
        self,
        candidate_name: str,
        role_title: str,
        strengths: List[ReasoningInsight],
        risks: List[ReasoningInsight],
        uncertainties: List[ReasoningInsight],
        match_result: Dict[str, Any],
    ) -> str:
        score = match_result.get("score")

        score_text = ""
        if score is not None:
            score_text = f" The current matching score is {score}."

        return (
            f"{candidate_name} shows a potentially relevant profile for the role of "
            f"{role_title}.{score_text} The strongest positive signals come from "
            f"{strengths[0].title.lower()}. The main point requiring attention is "
            f"{risks[0].title.lower()}. The analysis should be treated as decision support, "
            f"not as an automated hiring decision."
        )

    def _build_recommendation(
        self,
        strengths: List[ReasoningInsight],
        risks: List[ReasoningInsight],
        uncertainties: List[ReasoningInsight],
        match_result: Dict[str, Any],
    ) -> tuple[str, str]:
        score = match_result.get("score")

        if isinstance(score, (int, float)):
            if score >= 80:
                recommendation = "Strong candidate to interview"
            elif score >= 65:
                recommendation = "Candidate to consider with targeted validation"
            else:
                recommendation = "Candidate requires careful review before interview"
        else:
            recommendation = "Candidate requires qualitative review"

        rationale = (
            "This recommendation is based on the balance between documented strengths, "
            "identified risks, and remaining uncertainties. It should help the recruiter "
            "prioritize the next step, while keeping the final decision human-led."
        )

        return recommendation, rationale

    def _build_challenge(
        self,
        recommendation: str,
        risks: List[ReasoningInsight],
        uncertainties: List[ReasoningInsight],
    ) -> str:
        return (
            f"Although the recommendation is: '{recommendation}', it should be challenged. "
            f"The recruiter should pay particular attention to: {risks[0].title.lower()} "
            f"and {uncertainties[0].title.lower()}. A strong interview process should test "
            f"whether the evidence reflects real experience, ownership, and impact."
        )
