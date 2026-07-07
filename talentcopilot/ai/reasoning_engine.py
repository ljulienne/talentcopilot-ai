from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from talentcopilot.ai.evidence_intelligence import EvidenceIntelligenceEngine
from talentcopilot.ai.competency_reasoning import CompetencyReasoningEngine, CompetencyArgument


EVIDENCE_STRENGTH_SCORE = {
    "strong": 0.95,
    "moderate": 0.70,
    "weak": 0.40,
    "unknown": 0.25,
}


@dataclass
class ReasoningInsight:
    title: str
    explanation: str
    evidence: List[str] = field(default_factory=list)
    confidence: str = "medium"
    evidence_strength: str = "unknown"


@dataclass
class EvidenceAssessment:
    text: str
    strength: str
    interpretation: str
    confidence_score: float


@dataclass
class SkillAssessment:
    skill: str
    status: str
    explanation: str
    confidence_score: float
    evidence: List[str] = field(default_factory=list)


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
    evidence_assessment: List[EvidenceAssessment] = field(default_factory=list)
    skill_assessment: List[SkillAssessment] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    competency_arguments: List[CompetencyArgument] = field(default_factory=list)


class ReasoningEngine:
    """
    Evidence-first reasoning engine.

    Principles:
    - The engine supports decision-making; it does not make hiring decisions.
    - Conclusions must be tied to evidence whenever possible.
    - Missing evidence is treated as uncertainty, not as automatic rejection.
    - The engine remains generic and works across roles and industries.
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
        match_result = match_result or {}
        evidence = evidence or []

        evidence_assessment = self._assess_evidence(evidence)
        skill_assessment = self._assess_skills(candidate, job, evidence_assessment)
        missing_information = self._identify_missing_information(candidate, job, evidence_assessment)
        competency_arguments = self._build_competency_arguments(job, evidence_assessment)

        strengths = self._build_strengths(candidate, job, evidence_assessment, skill_assessment)
        risks = self._build_risks(candidate, job, skill_assessment)
        transferable_skills = self._build_transferable_skills(candidate, job, skill_assessment)
        uncertainties = self._build_uncertainties(candidate, evidence_assessment, missing_information)

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
            skill_assessment=skill_assessment,
            match_result=match_result,
        )

        challenge = self._build_challenge(
            recommendation=recommendation,
            risks=risks,
            uncertainties=uncertainties,
            missing_information=missing_information,
            competency_arguments=competency_arguments,
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
            evidence_assessment=evidence_assessment,
            skill_assessment=skill_assessment,
            missing_information=missing_information,
            competency_arguments=competency_arguments,
        )


    def _build_competency_arguments(
        self,
        job: Dict[str, Any],
        evidence_assessment: List[EvidenceAssessment],
    ) -> List[CompetencyArgument]:
        target_competencies = []

        for skill in job.get("required_skills", []) + job.get("preferred_skills", []):
            skill = str(skill)
            if skill not in target_competencies:
                target_competencies.append(skill)

        if not target_competencies:
            return []

        evidence_texts = [item.text for item in evidence_assessment]

        report = CompetencyReasoningEngine().analyze(
            evidence_texts=evidence_texts,
            target_competencies=target_competencies,
        )

        return report.arguments

    def _assess_evidence(self, evidence: List[Dict[str, Any]]) -> List[EvidenceAssessment]:
        assessments = []

        evidence_texts = []
        raw_items = []

        for item in evidence:
            text = str(item.get("text") or item.get("evidence") or "").strip()
            if not text:
                continue

            evidence_texts.append(text)
            raw_items.append(item)

        intelligence_report = EvidenceIntelligenceEngine().analyze(evidence_texts)
        intelligence_by_text = {
            item.text: item for item in intelligence_report.evidence_items
        }

        for item, text in zip(raw_items, evidence_texts):
            structured = intelligence_by_text.get(text)

            if structured and structured.quality:
                quality_score = structured.quality.score

                if quality_score >= 85:
                    strength = "strong"
                elif quality_score >= 70:
                    strength = "strong"
                elif quality_score >= 50:
                    strength = "moderate"
                else:
                    strength = "weak"

                confidence_score = quality_score / 100
                interpretation = (
                    f"{structured.explanation} "
                    f"Inferred competencies: {', '.join(structured.inferred_competencies) or 'not explicit'}. "
                    f"Limitations: {'; '.join(structured.limitations) or 'none detected'}."
                )
            else:
                strength = item.get("strength") or self._infer_evidence_strength(text)
                confidence_score = EVIDENCE_STRENGTH_SCORE.get(strength, 0.25)
                interpretation = self._interpret_evidence(text, strength)

            assessments.append(
                EvidenceAssessment(
                    text=text,
                    strength=strength,
                    interpretation=interpretation,
                    confidence_score=confidence_score,
                )
            )

        return assessments

    def _infer_evidence_strength(self, text: str) -> str:
        lower = text.lower()

        strong_indicators = [
            "led ",
            "managed ",
            "delivered ",
            "implemented ",
            "launched ",
            "owned ",
            "reduced ",
            "increased ",
            "improved ",
            "saved ",
            "generated ",
            "%",
            "€",
            "$",
            "team of",
            "across",
        ]

        weak_indicators = [
            "interested in",
            "familiar with",
            "exposure to",
            "basic knowledge",
            "participated in",
            "supported",
        ]

        if any(indicator in lower for indicator in strong_indicators):
            return "strong"

        if any(indicator in lower for indicator in weak_indicators):
            return "weak"

        return "moderate"

    def _interpret_evidence(self, text: str, strength: str) -> str:
        if strength == "strong":
            return (
                "This is a strong evidence item because it describes ownership, delivery, "
                "measurable impact, scale, or a concrete responsibility."
            )

        if strength == "moderate":
            return (
                "This is a moderate evidence item. It suggests relevant experience, but the "
                "level of ownership, scale, or impact should be clarified."
            )

        if strength == "weak":
            return (
                "This is a weak evidence item. It may indicate exposure or interest, but it "
                "does not prove practical ownership or impact."
            )

        return "The strength of this evidence is unclear and should be validated."

    def _assess_skills(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        evidence_assessment: List[EvidenceAssessment],
    ) -> List[SkillAssessment]:
        candidate_skills = {str(skill).lower(): str(skill) for skill in candidate.get("skills", [])}
        required_skills = [str(skill) for skill in job.get("required_skills", [])]
        preferred_skills = [str(skill) for skill in job.get("preferred_skills", [])]

        all_target_skills = []
        for skill in required_skills + preferred_skills:
            if skill not in all_target_skills:
                all_target_skills.append(skill)

        assessments = []

        for skill in all_target_skills:
            skill_lower = skill.lower()
            direct_match = skill_lower in candidate_skills
            evidence_hits = [
                ev for ev in evidence_assessment if skill_lower in ev.text.lower()
            ]

            if evidence_hits:
                best_score = max(ev.confidence_score for ev in evidence_hits)
                status = "demonstrated" if best_score >= 0.70 else "suggested"
                explanation = (
                    f"{skill} is supported by CV evidence. The strength of the conclusion "
                    "depends on the quality and specificity of the evidence."
                )
                assessments.append(
                    SkillAssessment(
                        skill=skill,
                        status=status,
                        explanation=explanation,
                        confidence_score=best_score,
                        evidence=[ev.text for ev in evidence_hits],
                    )
                )
            elif direct_match:
                assessments.append(
                    SkillAssessment(
                        skill=skill,
                        status="mentioned",
                        explanation=(
                            f"{skill} is mentioned in the candidate profile, but no concrete "
                            "supporting evidence was detected in the available evidence list."
                        ),
                        confidence_score=0.55,
                        evidence=[candidate_skills[skill_lower]],
                    )
                )
            else:
                assessments.append(
                    SkillAssessment(
                        skill=skill,
                        status="missing",
                        explanation=(
                            f"{skill} is required or useful for the role, but it is not clearly "
                            "visible in the candidate profile."
                        ),
                        confidence_score=0.20,
                        evidence=[],
                    )
                )

        return assessments

    def _identify_missing_information(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        evidence_assessment: List[EvidenceAssessment],
    ) -> List[str]:
        missing = []

        if not candidate.get("achievements"):
            missing.append("Business impact and measurable achievements are not sufficiently documented.")

        if not evidence_assessment:
            missing.append("Detailed CV evidence is missing or has not been extracted.")

        text_blob = " ".join(ev.text.lower() for ev in evidence_assessment)

        checks = {
            "Team size or scope of responsibility is unclear.": ["team of", "managed"],
            "Budget ownership is not documented.": ["budget", "€", "$"],
            "Decision-making authority is not clearly evidenced.": ["owned", "decided", "accountable"],
            "Stakeholder complexity is not clearly described.": ["stakeholder", "executive", "business partner"],
            "Measurable outcomes are limited or unclear.": ["increased", "reduced", "improved", "%", "saved"],
        }

        for message, indicators in checks.items():
            if not any(indicator in text_blob for indicator in indicators):
                missing.append(message)

        return missing

    def _build_strengths(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        evidence_assessment: List[EvidenceAssessment],
        skill_assessment: List[SkillAssessment],
    ) -> List[ReasoningInsight]:
        strengths = []

        demonstrated = [skill for skill in skill_assessment if skill.status == "demonstrated"]
        mentioned = [skill for skill in skill_assessment if skill.status == "mentioned"]

        if demonstrated:
            strengths.append(
                ReasoningInsight(
                    title="Demonstrated alignment with role requirements",
                    explanation=(
                        "Several target skills are supported by evidence rather than only being "
                        "listed as keywords. This increases the reliability of the match."
                    ),
                    evidence=[skill.skill for skill in demonstrated],
                    confidence="high",
                    evidence_strength="strong",
                )
            )

        if mentioned:
            strengths.append(
                ReasoningInsight(
                    title="Relevant skills mentioned in the profile",
                    explanation=(
                        "Some relevant skills are present in the profile, but they should be "
                        "validated because the available evidence does not fully demonstrate them."
                    ),
                    evidence=[skill.skill for skill in mentioned],
                    confidence="medium",
                    evidence_strength="moderate",
                )
            )

        strong_evidence = [ev.text for ev in evidence_assessment if ev.strength == "strong"]

        if strong_evidence:
            strengths.append(
                ReasoningInsight(
                    title="Concrete evidence of ownership or impact",
                    explanation=(
                        "The profile contains evidence items that suggest concrete ownership, "
                        "delivery, scale, or measurable impact."
                    ),
                    evidence=strong_evidence[:5],
                    confidence="high",
                    evidence_strength="strong",
                )
            )

        if not strengths:
            strengths.append(
                ReasoningInsight(
                    title="Limited explicit strengths detected",
                    explanation=(
                        "The available information does not provide enough explicit evidence to "
                        "identify strong role alignment."
                    ),
                    evidence=[],
                    confidence="low",
                    evidence_strength="unknown",
                )
            )

        return strengths

    def _build_risks(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        skill_assessment: List[SkillAssessment],
    ) -> List[ReasoningInsight]:
        risks = []

        missing_skills = [skill.skill for skill in skill_assessment if skill.status == "missing"]

        if missing_skills:
            risks.append(
                ReasoningInsight(
                    title="Potential gaps against target skills",
                    explanation=(
                        "Some required or preferred skills are not clearly visible in the candidate "
                        "profile. This should be treated as a validation point, not as automatic rejection."
                    ),
                    evidence=missing_skills,
                    confidence="medium",
                    evidence_strength="unknown",
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
                    evidence_strength="strong",
                )
            )

        if not risks:
            risks.append(
                ReasoningInsight(
                    title="No major risk detected from available data",
                    explanation=(
                        "No significant risk is immediately visible based on the structured data "
                        "currently available. Interview validation remains necessary."
                    ),
                    evidence=[],
                    confidence="medium",
                    evidence_strength="moderate",
                )
            )

        return risks

    def _build_transferable_skills(
        self,
        candidate: Dict[str, Any],
        job: Dict[str, Any],
        skill_assessment: List[SkillAssessment],
    ) -> List[ReasoningInsight]:
        preferred = set(job.get("preferred_skills", []))
        transferable = [
            skill for skill in skill_assessment
            if skill.skill in preferred and skill.status in {"demonstrated", "mentioned", "suggested"}
        ]

        if transferable:
            return [
                ReasoningInsight(
                    title="Additional transferable capabilities",
                    explanation=(
                        "The candidate shows capabilities that are not necessarily mandatory but "
                        "could increase contribution or adaptability in the role."
                    ),
                    evidence=[skill.skill for skill in transferable],
                    confidence="medium",
                    evidence_strength="moderate",
                )
            ]

        return [
            ReasoningInsight(
                title="Transferable skills require validation",
                explanation=(
                    "The current profile does not provide enough information to identify clear "
                    "transferable skills beyond the explicit matching criteria."
                ),
                evidence=[],
                confidence="low",
                evidence_strength="unknown",
            )
        ]

    def _build_uncertainties(
        self,
        candidate: Dict[str, Any],
        evidence_assessment: List[EvidenceAssessment],
        missing_information: List[str],
    ) -> List[ReasoningInsight]:
        uncertainties = []

        weak_evidence = [ev.text for ev in evidence_assessment if ev.strength == "weak"]

        if weak_evidence:
            uncertainties.append(
                ReasoningInsight(
                    title="Some conclusions rely on weak evidence",
                    explanation=(
                        "Parts of the profile suggest exposure rather than proven ownership. These "
                        "points should be tested during interviews."
                    ),
                    evidence=weak_evidence[:5],
                    confidence="medium",
                    evidence_strength="weak",
                )
            )

        if missing_information:
            uncertainties.append(
                ReasoningInsight(
                    title="Important information is still missing",
                    explanation=(
                        "The analysis identifies missing information that prevents a fully reliable "
                        "assessment of fit."
                    ),
                    evidence=missing_information[:6],
                    confidence="high",
                    evidence_strength="unknown",
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
                    evidence_strength="moderate",
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
        score_text = f" The current matching score is {score}." if score is not None else ""

        return (
            f"{candidate_name} shows a potentially relevant profile for the role of "
            f"{role_title}.{score_text} The strongest positive signal is "
            f"{strengths[0].title.lower()}. The main point requiring attention is "
            f"{risks[0].title.lower()}. Remaining uncertainty is mainly related to "
            f"{uncertainties[0].title.lower()}. This analysis is decision support and "
            f"must not replace recruiter judgment."
        )

    def _build_recommendation(
        self,
        strengths: List[ReasoningInsight],
        risks: List[ReasoningInsight],
        uncertainties: List[ReasoningInsight],
        skill_assessment: List[SkillAssessment],
        match_result: Dict[str, Any],
    ) -> tuple[str, str]:
        score = match_result.get("score")
        demonstrated_count = len([skill for skill in skill_assessment if skill.status == "demonstrated"])
        missing_count = len([skill for skill in skill_assessment if skill.status == "missing"])

        if isinstance(score, (int, float)):
            if score >= 80 and demonstrated_count >= missing_count:
                recommendation = "Strong candidate to interview"
            elif score >= 65:
                recommendation = "Candidate to consider with targeted validation"
            else:
                recommendation = "Candidate requires careful review before interview"
        else:
            if demonstrated_count > missing_count:
                recommendation = "Candidate to consider with targeted validation"
            else:
                recommendation = "Candidate requires qualitative review"

        rationale = (
            "The recommendation is based on the balance between demonstrated skills, missing "
            "requirements, evidence quality, and remaining uncertainty. The recruiter should use "
            "this recommendation to prioritize interviews, not to automate a hiring decision."
        )

        return recommendation, rationale

    def _build_challenge(
        self,
        recommendation: str,
        risks: List[ReasoningInsight],
        uncertainties: List[ReasoningInsight],
        missing_information: List[str],
        competency_arguments: List[CompetencyArgument] | None = None,
    ) -> str:
        missing_text = ""
        if missing_information:
            missing_text = f" Missing information to validate includes: {missing_information[0]}"

        return (
            f"Although the recommendation is: '{recommendation}', it should be challenged. "
            f"The recruiter should pay particular attention to {risks[0].title.lower()} and "
            f"{uncertainties[0].title.lower()}.{missing_text} A strong interview process should "
            f"test whether the evidence reflects real experience, ownership, and measurable impact."
        )
