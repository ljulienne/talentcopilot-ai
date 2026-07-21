from __future__ import annotations

import re
from typing import Iterable, List, Sequence, Tuple

from talentcopilot.mission_fit_v2.ontology import CONCEPTS, LABELS
from talentcopilot.recruitment_reasoning.models import (
    CriterionAssessment,
    MissionCriterion,
    RecruitmentReasoningResult,
)


class RecruitmentReasoningEngine:
    """Generic, evidence-led job/CV reasoning.

    The engine decomposes a job into weighted atomic criteria and assesses each
    criterion against direct and transferable CV evidence. It contains no
    candidate names, benchmark-specific scores, or hard-coded ranking order.
    """

    version = "recruitment-reasoning-v1.1.1-evidence-prioritisation"

    CATEGORY_WEIGHTS = {
        "function": 0.20,
        "capability": 0.28,
        "tool": 0.16,
        "experience": 0.14,
        "leadership": 0.08,
        "language": 0.06,
        "education": 0.04,
        "context": 0.04,
    }

    # Generic requirement patterns that commonly express evidence beyond a
    # simple skill keyword. They apply across job families.
    BEHAVIOURAL_CRITERIA = (
        ("testing", "Testing / acceptance", "capability", ("acceptance testing", "user acceptance testing", "uat", "sit", "functional testing", "technical testing", "testing"), ("quality assurance", "validation")),
        ("data_quality", "Data quality / reliability", "capability", ("data cleaning", "data quality", "data reliability", "data integrity", "data governance"), ("data accuracy", "master data")),
        ("vendor_management", "Vendor / provider management", "capability", ("vendor management", "provider management", "integrator management", "manage relationships with", "solution providers", "managed vendors", "manage vendors"), ("supplier management", "consulting partners")),
        ("budget_management", "Budget / resource management", "capability", ("budget", "resources", "resource planning", "cost management"), ("p&l", "financial planning")),
        ("steering_governance", "Steering and governance", "capability", ("steering committee", "project committee", "governance", "risk management", "corrective action plan"), ("executive reporting", "project oversight")),
        ("people_leadership", "People leadership", "leadership", ("manage and support", "manage a team", "managed a team", "led a team", "supervised", "coach", "mentoring", "people management"), ("functional team management", "team leadership")),
        ("change_adoption", "Change and user adoption", "capability", ("change management", "user adoption", "training plan", "communication plan", "upskilling", "post-deployment support"), ("training", "communications", "support")),
        ("integration", "Systems integration / interfaces", "capability", ("interface", "interfaces", "integration", "api", "third-party systems", "web service"), ("system migration", "cloud migration")),
        ("reporting_analytics", "Reporting and analytics", "capability", ("reporting", "dashboard", "kpi", "analytics", "business intelligence"), ("data analysis", "management reporting")),
        ("core_platform", "Core platform deployment", "capability", ("core hr", "core platform", "employee central", "system implementation", "platform deployment"), ("employee data", "personnel administration")),
        ("ai_innovation", "AI / digital innovation", "context", ("artificial intelligence", " ai ", "machine learning", "automation"), ("digital transformation", "digitization")),
    )

    TRANSFERABLE_TOOL_GROUPS = (
        {"tool_successfactors", "tool_workday", "tool_oracle_hcm", "tool_talentsoft", "tool_sap"},
        {"tool_power_bi", "tool_excel", "tool_sql", "tool_python"},
    )

    def evaluate(self, job_text: str, candidate_text: str, candidate_name: str = "Candidate") -> RecruitmentReasoningResult:
        job = self._normalise(job_text)
        candidate = self._normalise(candidate_text)
        criteria = self._build_criteria(job)
        assessments = [self._assess(item, candidate) for item in criteria]

        total_weight = sum(item.criterion.weight for item in assessments) or 1.0
        score = sum(item.contribution for item in assessments) / total_weight

        mandatory = [item for item in assessments if item.criterion.mandatory]
        mandatory_gaps = [item for item in mandatory if item.evidence_score < 0.45]
        if mandatory_gaps:
            score -= min(14.0, 4.0 * len(mandatory_gaps))

        score = round(max(0.0, min(100.0, score)), 2)
        evidenced = sum(1 for item in assessments if item.evidence_score >= 0.45)
        confidence = int(max(48, min(96, 52 + evidenced * 4 + min(len(criteria), 8))))

        strengths = [
            self._strength_statement(item)
            for item in sorted(assessments, key=self._evidence_priority, reverse=True)
            if item.evidence and item.evidence_score >= 0.7
        ][:8]
        gaps = [
            self._gap_statement(item)
            for item in sorted(assessments, key=lambda value: (value.criterion.mandatory, value.criterion.weight), reverse=True)
            if item.evidence_score < 0.7
        ][:10]

        recommendation, risk = self._decision(score, len(mandatory_gaps), confidence)
        rationale = self._rationale(
            candidate_name, score, recommendation, risk, confidence, strengths, gaps, assessments
        )
        return RecruitmentReasoningResult(
            score=score,
            confidence=confidence,
            recommendation=recommendation,
            risk_level=risk,
            criteria=criteria,
            assessments=assessments,
            strengths=strengths,
            gaps=gaps,
            rationale=rationale,
            version=self.version,
        )

    def _build_criteria(self, job: str) -> List[MissionCriterion]:
        criteria: List[MissionCriterion] = []

        concept_categories = {
            "function_": "function",
            "skill_": "capability",
            "commercial_": "capability",
            "tool_": "tool",
            "leadership_": "leadership",
            "language_": "language",
            "education_": "education",
            "geography_": "context",
            "industry_": "context",
        }
        concept_alias_overrides = {
            "skill_project_management": ("project manager", "program manager", "project lead", "programme manager"),
            "leadership_people": ("manage a collaborator", "manage an employee", "support a collaborator", "direct reports"),
        }
        for concept, aliases in CONCEPTS.items():
            effective_aliases = tuple(aliases) + tuple(concept_alias_overrides.get(concept, ()))
            if not any(self._contains(job, alias) for alias in effective_aliases):
                continue
            category = next((value for prefix, value in concept_categories.items() if concept.startswith(prefix)), "capability")
            criteria.append(MissionCriterion(
                key=concept,
                label=LABELS.get(concept, concept.replace("_", " ").title()),
                category=category,
                weight=self.CATEGORY_WEIGHTS[category],
                mandatory=self._is_mandatory(job, effective_aliases),
                aliases=list(effective_aliases),
                transferable_aliases=self._transferable_aliases(concept),
            ))

        for key, label, category, aliases, transferable in self.BEHAVIOURAL_CRITERIA:
            if any(self._contains(job, alias) for alias in aliases):
                criteria.append(MissionCriterion(
                    key=key,
                    label=label,
                    category=category,
                    weight=self.CATEGORY_WEIGHTS[category],
                    mandatory=self._is_mandatory(job, aliases),
                    aliases=list(aliases),
                    transferable_aliases=list(transferable),
                ))

        minimum_years = self._minimum_years(job)
        if minimum_years:
            criteria.append(MissionCriterion(
                key="minimum_experience",
                label=f"Minimum {minimum_years} years of relevant experience",
                category="experience",
                weight=self.CATEGORY_WEIGHTS["experience"],
                mandatory=True,
                aliases=[str(minimum_years)],
            ))

        # Deduplicate and distribute category weight over the criteria actually
        # present in the job. This keeps the engine generic and prevents long job
        # descriptions from inflating a category.
        unique = {item.key: item for item in criteria}
        criteria = list(unique.values())
        counts = {}
        for item in criteria:
            counts[item.category] = counts.get(item.category, 0) + 1
        for item in criteria:
            item.weight = self.CATEGORY_WEIGHTS[item.category] / counts[item.category]
            if item.mandatory:
                item.weight *= 1.6
        total = sum(item.weight for item in criteria) or 1.0
        for item in criteria:
            item.weight /= total
        return criteria

    def _assess(self, criterion: MissionCriterion, candidate: str) -> CriterionAssessment:
        if criterion.key == "minimum_experience":
            required = int(criterion.aliases[0])
            evidenced = self._candidate_years(candidate)
            ratio = min(1.0, evidenced / required) if required else 1.0
            level = "direct" if ratio >= 1 else "partial" if ratio >= 0.65 else "weak" if ratio > 0 else "none"
            evidence = [f"{evidenced} years evidenced against {required} required"] if evidenced else []
            gaps = [] if ratio >= 1 else [f"Experience threshold not fully evidenced ({evidenced}/{required} years)"]
            return CriterionAssessment(criterion, level, ratio, criterion.weight * ratio * 100, evidence, gaps)

        direct = [alias for alias in criterion.aliases if self._contains(candidate, alias)]
        transferable = [alias for alias in criterion.transferable_aliases if self._contains(candidate, alias)]
        if direct:
            evidence_score, level = 1.0, "direct"
            evidence = [f"Direct evidence: {direct[0]}"]
        elif transferable:
            evidence_score, level = 0.72, "transferable"
            evidence = [f"Transferable evidence: {transferable[0]}"]
        else:
            evidence_score, level = 0.0, "none"
            evidence = []

        gaps = [] if evidence else [
            f"The available CV does not provide sufficient evidence to confirm {criterion.label}."
        ]
        return CriterionAssessment(
            criterion=criterion,
            evidence_level=level,
            evidence_score=evidence_score,
            contribution=criterion.weight * evidence_score * 100,
            evidence=evidence,
            gaps=gaps,
        )

    def _transferable_aliases(self, concept: str) -> List[str]:
        aliases: List[str] = []
        for group in self.TRANSFERABLE_TOOL_GROUPS:
            if concept in group:
                for peer in sorted(group - {concept}):
                    aliases.extend(CONCEPTS.get(peer, ()))
        return sorted(dict.fromkeys(aliases), key=str.casefold)

    def _is_mandatory(self, job: str, aliases: Sequence[str]) -> bool:
        markers = ("essential", "required", "must", "minimum", "mandatory", "requis", "indispensable", "essentiel")
        for alias in aliases:
            for match in re.finditer(re.escape(alias), job, re.I):
                window = job[max(0, match.start() - 90): match.end() + 90]
                if any(marker in window for marker in markers):
                    return True
        return False

    def _minimum_years(self, text: str) -> int:
        values = [int(value) for value in re.findall(r"(?:minimum(?: of)?|at least|au moins|minimum de)?\s*(\d{1,2})\s*\+?\s*(?:years?|ans?)", text, re.I)]
        return max(values, default=0)

    def _candidate_years(self, text: str) -> int:
        explicit = [int(value) for value in re.findall(r"(\d{1,2})\s*\+?\s*(?:years?|ans?)", text, re.I) if int(value) <= 50]
        years = [int(value) for value in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
        if len(years) >= 2:
            explicit.append(max(years) - min(years))
        return max(explicit, default=0)

    def _decision(self, score: float, mandatory_gaps: int, confidence: int) -> Tuple[str, str]:
        """Calibrate decision risk without treating a mid-range score as high risk by default."""
        if score >= 84 and not mandatory_gaps:
            return "Strong Hire", "Low"
        if score >= 70:
            return "Interview", "Low" if not mandatory_gaps else "Medium"
        if score >= 56:
            return "More Evidence Required", "Medium"
        if score >= 40:
            risk = "High" if mandatory_gaps >= 2 and confidence < 65 else "Medium"
            return "Review", risk
        return "Reject", "Critical" if mandatory_gaps >= 2 else "High"


    def _evidence_priority(self, assessment: CriterionAssessment) -> tuple[float, float, float, str]:
        """Rank evidence for advisory writing without changing the official score.

        The matching score remains weight-based.  This separate presentation
        ranking prevents eligibility checks such as tenure from being described
        as the candidate's most compelling differentiator.
        """
        category_priority = {
            "capability": 7.0,
            "tool": 6.5,
            "leadership": 5.5,
            "function": 5.0,
            "context": 4.0,
            "language": 2.5,
            "education": 2.0,
            "experience": 1.0,
        }
        key = assessment.criterion.key
        label = assessment.criterion.label.casefold()
        achievement_bonus = 0.0
        if any(token in label for token in (
            "implementation", "deployment", "transformation", "migration",
            "integration", "governance", "analytics", "adoption", "testing",
            "project", "platform", "data quality", "vendor", "budget",
        )):
            achievement_bonus = 1.0
        ownership_bonus = 0.5 if assessment.criterion.mandatory else 0.0
        # Explicitly demote minimum tenure: it establishes viability, not
        # differentiated fit.
        eligibility_penalty = -3.0 if key == "minimum_experience" else 0.0
        return (
            category_priority.get(assessment.criterion.category, 3.0)
            + achievement_bonus
            + ownership_bonus
            + eligibility_penalty,
            assessment.evidence_score,
            assessment.contribution,
            assessment.criterion.label.casefold(),
        )

    def _strength_statement(self, assessment: CriterionAssessment) -> str:
        label = self._professional_label(assessment.criterion.label)
        evidence = assessment.evidence[0] if assessment.evidence else ""
        evidence = re.sub(r"^(Direct|Transferable) evidence:\s*", "", evidence, flags=re.I)
        evidence = self._professional_label(evidence)
        if assessment.criterion.key == "minimum_experience":
            return (
                f"The profile clearly meets the required level of seniority "
                f"({evidence}), supporting role readiness without being a differentiator on its own."
            )
        if assessment.evidence_level == "transferable":
            return (
                f"Transferable experience in {evidence} provides credible support for {label}, "
                "although direct ownership should still be confirmed."
            )
        return f"Direct evidence of {evidence} supports the candidate's capability in {label}."

    def _professional_label(self, value: str) -> str:
        text = re.sub(r"\s+", " ", str(value or "")).strip(" .;:-")
        text = re.sub(r"^(tool|function|skill|requirement)\s+", "", text, flags=re.I)
        replacements = {
            "sap": "SAP",
            "sap successfactors": "SAP SuccessFactors",
            "power bi": "Power BI",
            "hris": "HRIS",
            "api": "API",
            "uat": "UAT",
        }
        lowered = text.casefold()
        return replacements.get(lowered, text)

    def _gap_statement(self, assessment: CriterionAssessment) -> str:
        label = assessment.criterion.label
        if assessment.evidence_level == "transferable":
            return (
                f"{label} is only partially evidenced through transferable experience; "
                "the interview should confirm direct ownership and operating depth."
            )
        importance = "role-critical " if assessment.criterion.mandatory else ""
        return (
            f"The available CV does not provide sufficient evidence to confirm the {importance}"
            f"requirement for {label}. This is an evidence uncertainty, not a confirmed capability gap."
        )

    def _rationale(
        self,
        name: str,
        score: float,
        recommendation: str,
        risk: str,
        confidence: int,
        strengths: List[str],
        gaps: List[str],
        assessments: List[CriterionAssessment],
    ) -> str:
        direct_count = sum(item.evidence_level == "direct" for item in assessments)
        transferable_count = sum(item.evidence_level == "transferable" for item in assessments)
        mandatory_uncertainties = [
            item for item in assessments
            if item.criterion.mandatory and item.evidence_score < 0.45
        ]

        if score >= 80:
            opening = "is a strong, credible match for the role"
        elif score >= 65:
            opening = "is a credible match, with several points that require validation"
        elif score >= 45:
            opening = "is a plausible but incomplete match"
        else:
            opening = "shows limited alignment with the role on the evidence currently available"

        paragraphs = [
            f"{name} {opening}. The official Mission Fit is {score:.0f}%, with {confidence}% evidence confidence."
        ]

        differentiators = [item for item in strengths if "meets the required level of seniority" not in item.casefold()]
        eligibility = [item for item in strengths if item not in differentiators]
        if differentiators:
            paragraphs.append(
                "The most compelling evidence comes from "
                + self._join_sentences(differentiators[:3])
            )
        elif eligibility:
            paragraphs.append(
                self._join_sentences(eligibility[:1])
                + " The available CV otherwise offers limited differentiated evidence against the role's core capabilities."
            )
        else:
            paragraphs.append(
                "The CV contains limited directly verifiable evidence against the role's most important capabilities."
            )

        if gaps:
            paragraphs.append(
                "The principal decision uncertainties concern "
                + self._join_sentences(gaps[:3])
            )

        evidence_summary = (
            f"Across the assessment, {direct_count} requirement(s) are directly evidenced and "
            f"{transferable_count} are supported through transferable experience."
        )
        if mandatory_uncertainties:
            evidence_summary += (
                f" {len(mandatory_uncertainties)} mandatory requirement(s) still require explicit validation."
            )
        paragraphs.append(evidence_summary)

        if recommendation in {"Strong Hire", "Hire"}:
            action = "Proceed, while using the interview to confirm the remaining role-critical uncertainties."
        elif recommendation == "Interview":
            action = "Proceed to a structured interview focused on direct ownership, operating depth and demonstrated impact."
        elif recommendation in {"More Evidence Required", "Review"}:
            action = (
                "Keep the candidate under consideration, but defer a final decision until the interview has established "
                "direct ownership, operating scope and measurable outcomes in the uncertain areas."
            )
        else:
            action = "Do not progress unless materially stronger evidence changes the current assessment."

        paragraphs.append(f"The current recommendation is {recommendation}, with {risk.lower()} hiring risk. {action}")
        return "\n\n".join(paragraphs)

    def _join_sentences(self, values: Sequence[str]) -> str:
        cleaned = [str(value).strip().rstrip(".") for value in values if str(value).strip()]
        if not cleaned:
            return ""
        if len(cleaned) == 1:
            return cleaned[0] + "."
        if len(cleaned) == 2:
            return cleaned[0] + "; and " + cleaned[1][0].lower() + cleaned[1][1:] + "."
        return "; ".join(cleaned[:-1]) + "; and " + cleaned[-1][0].lower() + cleaned[-1][1:] + "."

    def _contains(self, text: str, phrase: str) -> bool:
        phrase = str(phrase or "").strip()
        if not phrase:
            return False
        escaped = re.escape(phrase)
        # Permit ordinary English plural forms for a one-word concept (API/APIs,
        # dashboard/dashboards) without turning the matcher into fuzzy search.
        if " " not in phrase and phrase[-1:].isalpha() and not phrase.endswith("s"):
            escaped += "s?"
        return bool(re.search(r"(?<!\w)" + escaped + r"(?!\w)", text, re.I))

    def _normalise(self, value: str) -> str:
        return " " + " ".join(str(value or "").replace("’", "'").lower().split()) + " "
