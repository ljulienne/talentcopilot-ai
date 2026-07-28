from __future__ import annotations

from typing import Iterable, Optional
import re

from talentcopilot.interview.models import InterviewCompetency, InterviewQuestion


class InterviewQuestionService:
    """Build varied evidence-grounded questions without an LLM call."""

    ENGINE_VERSION = "7.6.0-technical-requirement-intelligence"

    _INTERNAL_EVIDENCE_LABELS = {
        "management scope",
        "project ownership",
        "budget responsibility",
        "tool exposure",
        "measurable impact",
        "leadership scope",
        "stakeholder complexity",
        "technical depth",
        "process design",
        "governance exposure",
    }

    def build(
        self,
        competencies: list[InterviewCompetency],
        *,
        role_title: str = "the role",
        candidate: Optional[dict] = None,
        mission_requirements: Optional[Iterable[str]] = None,
    ) -> list[InterviewQuestion]:
        candidate = candidate or {}
        requirements = [
            str(item).strip()
            for item in (mission_requirements or [])
            if str(item).strip()
        ]
        achievements = self._candidate_evidence_lines(candidate)
        candidate_skills = [
            str(item).strip()
            for item in candidate.get("skills", [])
            if str(item).strip()
        ]
        years = candidate.get("years_experience", 0)

        target = [c for c in competencies if c.validate_in_interview]
        if not target:
            target = competencies[:3]

        return [
            self._build_question(
                competency,
                role_title=role_title,
                requirements=requirements,
                achievements=achievements,
                candidate_skills=candidate_skills,
                years=years,
                index=index,
            )
            for index, competency in enumerate(target[:6])
        ]

    def _build_question(
        self,
        competency: InterviewCompetency,
        *,
        role_title: str,
        requirements: list[str],
        achievements: list[str],
        candidate_skills: list[str],
        years,
        index: int,
    ) -> InterviewQuestion:
        name = competency.name
        requirement = self._matching_requirement(name, requirements) or name
        evidence, evidence_type = self._grounded_evidence(
            name,
            achievements=achievements,
            candidate_skills=candidate_skills,
        )
        declared_status = str(getattr(competency, "evidence_status", "") or "")
        if declared_status == "No direct evidence":
            evidence_type = "gap"
        elif declared_status == "Related evidence":
            evidence_type = "related"
        elif declared_status == "Direct evidence" and evidence_type == "gap":
            evidence_type = "inference"
        related_evidence = list(getattr(competency, "related_evidence", []) or [])
        archetype = self._archetype(name, index)

        question, expected, positives, warnings, follow_ups = self._question_pack(
            archetype=archetype,
            competency=name,
            requirement=requirement,
            evidence=evidence,
            evidence_type=evidence_type,
            role_title=role_title,
            related_evidence=related_evidence,
        )

        experience_note = (
            f" The CV indicates approximately {years:g} years of experience."
            if isinstance(years, (int, float)) and years
            else ""
        )
        rationale = competency.rationale or "Current evidence requires interview validation."

        return InterviewQuestion(
            competency=name,
            question=question,
            objective=(
                f"Resolve the decision uncertainty around {name} using a {archetype.replace('_', ' ')} lens."
                f"{experience_note} Current evidence position: {rationale} "
                "The answer should distinguish personal ownership from team contribution and connect actions to a measurable outcome."
            ),
            expected_evidence=expected,
            positive_signals=positives,
            warning_signals=warnings,
            follow_ups=follow_ups,
        )

    def _question_pack(
        self,
        *,
        archetype: str,
        competency: str,
        requirement: str,
        evidence: str,
        evidence_type: str,
        role_title: str,
        related_evidence: list[str] | None = None,
    ):
        prefix = self._evidence_prefix(
            competency=competency,
            requirement=requirement,
            evidence=evidence,
            evidence_type=evidence_type,
        )

        normalized_competency = competency.casefold()
        related_label = ", ".join((related_evidence or [])[:4])

        if "successfactors" in normalized_competency:
            if evidence_type in {"gap", "related"}:
                transfer = (
                    f" Related HRIS experience was identified ({related_label})."
                    if related_label else ""
                )
                return (
                    prefix + transfer + " " +
                    "The role requires strong SAP SuccessFactors and Core HR expertise. "
                    "Describe any direct SuccessFactors experience that may be absent from the CV, including the systems, modules, interfaces and data flows involved. "
                    "If you have none, explain which HRIS platform experience is genuinely transferable, "
                    "which SuccessFactors modules you would need to master, and how you would de-risk a Core HR deployment.",
                    [
                        "Exact SuccessFactors modules and release scope, if any",
                        "Personal configuration, migration or deployment responsibility",
                        "Concrete comparison with another HRIS platform",
                        "A credible learning and delivery risk-mitigation plan",
                    ],
                    [
                        "Distinguishes direct product expertise from transferable HRIS experience",
                        "Names Employee Central or other relevant modules precisely",
                        "Explains data, integration and testing implications",
                    ],
                    [
                        "Claims generic HRIS experience as equivalent product mastery",
                        "Cannot name modules or platform-specific delivery risks",
                        "Provides no credible transfer or upskilling plan",
                    ],
                    [
                        "Which SuccessFactors module would create the steepest learning curve for you?",
                        "How would you validate a Core HR data model before migration?",
                        "Which prior platform decisions would not transfer to SuccessFactors?",
                    ],
                )

        if "power bi" in normalized_competency:
            return (
                prefix +
                "The role requires dynamic Power BI reporting from Core HR data. "
                "Describe the most advanced Power BI solution you personally delivered: which source data and source systems, "
                "data model, Power Query or DAX logic, security controls and HR KPIs did you own, and what decision changed because of the dashboard?",
                [
                    "Source systems and refresh architecture",
                    "Personal ownership of Power Query, modelling or DAX",
                    "Data-quality and access-control checks",
                    "Decision impact and adoption metrics",
                ],
                [
                    "Explains hands-on technical contribution rather than only sponsorship",
                    "Connects Core HR data lineage to KPI definitions",
                    "Describes validation, security and user adoption",
                ],
                [
                    "Mentions Power BI only as a viewer or project label",
                    "Cannot explain the data model or KPI calculation",
                    "No evidence of data-quality validation",
                ],
                [
                    "Which DAX measure or transformation was the most complex?",
                    "How did you reconcile dashboard results with the source HRIS?",
                    "What measurable decision or process improvement followed?",
                ],
            )

        if "ai solutions" in normalized_competency or "artificial intelligence" in normalized_competency:
            return (
                prefix +
                "The role includes developing AI solutions for HR processes. "
                "Describe any AI, machine-learning or generative-AI use case you have personally helped design or deploy. "
                "If you have not deployed one, propose a realistic HR use case and explain the data, privacy, bias, explainability, human-oversight and success-measure requirements.",
                [
                    "Specific HR problem and users",
                    "Data inputs, model or solution approach",
                    "Privacy, bias and human-oversight controls",
                    "Pilot success metrics and deployment decision",
                ],
                [
                    "Separates analytics, automation and genuine AI",
                    "Defines a bounded use case with measurable value",
                    "Addresses governance and human accountability",
                ],
                [
                    "Uses AI as a vague label with no operating model",
                    "Ignores sensitive HR data and bias risks",
                    "Cannot define validation or success metrics",
                ],
                [
                    "Which HR decision should never be fully automated?",
                    "How would you test bias before a pilot goes live?",
                    "Which metric would justify scaling the solution?",
                ],
            )

        if archetype == "technical":
            return (
                prefix
                + f"Describe the most technically demanding {competency} situation you handled. "
                  "Which systems, modules, interfaces or data flows were involved, "
                  "which technical decisions did you personally make, how did you validate the solution, "
                  "what defect or limitation was hardest to resolve, and which measurable reliability, quality, or delivery result improved?",
                [
                    "Specific systems, modules and configuration scope",
                    "Testing or validation approach",
                    "Concrete technical constraint and resolution",
                    "Evidence of production quality or stability",
                ],
                [
                    "Shows clear technical ownership of design and configuration decisions",
                    "Explains architecture, configuration and validation precisely",
                    "Distinguishes design choices from vendor defaults",
                    "Shows diagnostic depth and technical accountability",
                ],
                [
                    "Cannot name the systems or modules involved",
                    "Describes only coordination with no technical understanding",
                    "No evidence of testing or quality controls",
                ],
                [
                    "Which interface or data dependency created the highest risk?",
                    "What did you reject or redesign, and why?",
                    "Which test result or production metric confirmed that your solution worked?",
                ],
            )

        if archetype == "data":
            return (
                prefix
                + f"Describe a {competency} deliverable that influenced an HR or business decision. "
                  "What source data did you personally validate, how did you ensure reliability, "
                  "which KPI mattered most, what measurable change did the analysis reveal, and what decision changed because of it?",
                [
                    "Source systems and data model",
                    "Data-quality controls",
                    "Relevant KPI definition",
                    "Decision or action enabled",
                ],
                [
                    "Shows clear ownership of data validation and KPI definitions",
                    "Explains lineage and validation checks",
                    "Chooses KPIs tied to a business decision",
                    "Shows how stakeholders used the output",
                ],
                [
                    "Focuses only on dashboard appearance",
                    "Cannot explain data quality or KPI definitions",
                    "No evidence that the analysis changed a decision",
                ],
                [
                    "Which data-quality issue could have changed the conclusion?",
                    "How did you prevent users from misinterpreting the KPI?",
                    "Which stakeholder decision was directly influenced by the result?",
                ],
            )

        if archetype == "change":
            return (
                prefix
                + f"Choose one transformation where adoption of {competency} was uncertain. "
                  "Which user groups resisted, what did you personally change in the communication or training approach, "
                  "and which measurable adoption or behavioural indicator proved that the change worked?",
                [
                    "Stakeholder segmentation",
                    "Resistance diagnosis",
                    "Targeted change actions",
                    "Adoption metrics or behavioural evidence",
                ],
                [
                    "Shows clear ownership of the change strategy and adoption actions",
                    "Names distinct populations and resistance patterns",
                    "Links interventions to measured adoption",
                    "Shows adaptation rather than generic communication",
                ],
                [
                    "Relies only on training attendance",
                    "Cannot explain resistance or stakeholder differences",
                    "No measurable adoption outcome",
                ],
                [
                    "Which population required a different approach?",
                    "What early signal showed the change plan was not working?",
                    "Which adoption metric improved after you changed the approach?",
                ],
            )

        if archetype == "stakeholder":
            return (
                prefix
                + f"For the {role_title} context, describe a situation where stakeholders had "
                  f"conflicting priorities around {competency}. Who disagreed, "
                  "how did you personally influence the decision, what framework did you use, "
                  "how did you secure commitment, and what measurable delivery or business outcome followed?",
                [
                    "Stakeholder map and competing interests",
                    "Decision criteria",
                    "Influencing approach",
                    "Documented agreement or governance outcome",
                ],
                [
                    "Shows clear ownership of stakeholder alignment and final decision-making",
                    "Explains power dynamics and competing incentives",
                    "Uses explicit criteria to arbitrate",
                    "Secures a concrete commitment or governance decision",
                ],
                [
                    "Avoids conflict rather than resolving it",
                    "Escalates without attempting influence",
                    "Cannot explain the final decision rationale",
                ],
                [
                    "Which stakeholder had the strongest veto power?",
                    "What concession did you make, and what did you protect?",
                    "How did you verify that the final commitment was translated into action?",
                ],
            )

        if archetype == "leadership":
            return (
                prefix
                + f"Give an example where you had to develop or redirect another person while "
                  f"delivering {competency}. What capability gap did you personally identify, "
                  "what did you delegate, and which measurable performance or autonomy indicator improved?",
                [
                    "Initial capability or performance gap",
                    "Delegation and coaching approach",
                    "Feedback cadence",
                    "Observable performance improvement",
                ],
                [
                    "Shows clear ownership of team development and performance improvement",
                    "Adapts coaching to the individual",
                    "Delegates meaningful responsibility with controls",
                    "Shows measurable improvement or independence",
                ],
                [
                    "Equates management with task assignment",
                    "No feedback or development approach",
                    "Cannot describe the person's progress",
                ],
                [
                    "What did you stop doing personally once the person improved?",
                    "How did you handle underperformance?",
                    "Which measurable behaviour showed that the person had become more autonomous?",
                ],
            )

        if archetype == "risk":
            return (
                prefix
                + f"Describe the highest-risk situation you encountered in {competency}. "
                  "Which early warning indicators did you personally monitor, what mitigation options "
                  "did you compare, what residual risk did you accept, and what measurable impact did the mitigation prevent or reduce?",
                [
                    "Risk statement and impact",
                    "Early warning indicators",
                    "Alternative mitigations",
                    "Residual-risk decision",
                ],
                [
                    "Shows clear ownership of risk identification, mitigation and escalation",
                    "Quantifies probability and impact",
                    "Compares options and trade-offs",
                    "Escalates with a recommendation, not just a problem",
                ],
                [
                    "Identifies the risk only after it materialised",
                    "No alternative options considered",
                    "Cannot explain residual risk acceptance",
                ],
                [
                    "Which mitigation did you reject and why?",
                    "At what threshold would you have escalated differently?",
                    "Which indicator confirmed that the residual risk remained acceptable?",
                ],
            )

        return (
            prefix
            + f"Describe one example that best proves your personal contribution to {competency}. "
              "What responsibility did you personally own, what did you deliver, "
              "and which measurable result was used to assess success?",
            [
                "Personal accountability",
                "Concrete deliverable",
                "Decision or action taken",
                "Outcome assessment",
            ],
            [
                "Shows clear ownership of the deliverable and its outcome",
                "Separates personal contribution from team activity",
                "Uses evidence to demonstrate impact",
            ],
            [
                "Uses only collective language",
                "Cannot identify a personal deliverable",
                "No objective success measure",
            ],
            [
                "What would not have happened without your contribution?",
                "Who can verify the result?",
                "Which measurable outcome is most directly attributable to your work?",
            ],
        )

    def _archetype(self, competency: str, index: int) -> str:
        value = competency.lower()
        if any(token in value for token in ("power bi", "analytics", "report", "data", "dashboard")):
            return "data"
        if any(token in value for token in ("change", "adoption", "training", "transformation")):
            return "change"
        if any(token in value for token in ("stakeholder", "vendor", "committee", "communication")):
            return "stakeholder"
        if any(token in value for token in ("management", "leadership", "coaching", "team")):
            return "leadership"
        if any(token in value for token in ("risk", "quality", "compliance", "governance")):
            return "risk"
        if any(token in value for token in ("hris", "core hr", "successfactors", "interface", "integration", "testing")):
            return "technical"
        return ("ownership", "risk", "stakeholder")[index % 3]

    def _matching_requirement(self, competency: str, requirements: list[str]) -> str:
        needle = competency.lower()
        for requirement in requirements:
            lower = requirement.lower()
            if needle in lower or lower in needle:
                return requirement
        return ""

    def _candidate_evidence_lines(self, candidate: dict) -> list[str]:
        lines: list[str] = []
        raw_text = str(candidate.get("raw_text") or "").strip()
        if raw_text:
            lines.extend(
                " ".join(line.split())
                for line in raw_text.splitlines()
                if len(" ".join(line.split())) >= 12
            )
        for key in ("achievements", "responsibilities", "experience", "experiences"):
            value = candidate.get(key, [])
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, (list, tuple)):
                continue
            for item in value:
                if isinstance(item, dict):
                    for field in ("description", "summary", "responsibilities", "achievements"):
                        nested = item.get(field)
                        if isinstance(nested, str):
                            lines.append(nested.strip())
                        elif isinstance(nested, (list, tuple)):
                            lines.extend(str(entry).strip() for entry in nested if str(entry).strip())
                elif str(item).strip():
                    lines.append(str(item).strip())
        return list(dict.fromkeys(line for line in lines if line))

    def _grounded_evidence(
        self,
        competency: str,
        *,
        achievements: list[str],
        candidate_skills: list[str],
    ) -> tuple[str, str]:
        exact_phrases = self._evidence_phrases(competency)
        exact_matching = [
            item for item in achievements
            if any(phrase in item.casefold() for phrase in exact_phrases)
        ]
        for item in exact_matching:
            if self._is_verbatim_evidence(item):
                phrase = next(
                    (value for value in exact_phrases if value in item.casefold()),
                    exact_phrases[0] if exact_phrases else "",
                )
                return self._excerpt_around(item, phrase), "verbatim"

        tokens = self._tokens(competency)
        matching = [
            item for item in achievements
            if tokens and any(token in item.casefold() for token in tokens)
        ]
        for item in matching:
            if self._is_verbatim_evidence(item):
                return item, "verbatim"

        skill_match = any(
            self._concepts_overlap(competency, skill)
            for skill in candidate_skills
        )
        if skill_match or matching:
            return competency, "inference"
        return "", "gap"

    def _evidence_phrases(self, competency: str) -> tuple[str, ...]:
        value = competency.casefold()
        if "power bi" in value:
            return ("power bi", "powerbi")
        if "successfactors" in value:
            return ("successfactors", "success factors")
        if "ai solutions" in value or "artificial intelligence" in value:
            return ("artificial intelligence", "generative ai", "machine learning", " ai ")
        if "interfaces" in value or "technical delivery" in value:
            return ("interface", "integration", "sit", "uat", "acceptance testing")
        if "data quality" in value:
            return ("data quality", "data accuracy", "data integrity", "data reliability")
        return ()

    def _evidence_prefix(
        self,
        *,
        competency: str,
        requirement: str,
        evidence: str,
        evidence_type: str,
    ) -> str:
        if evidence_type == "verbatim":
            return f"Your CV states: ‘{self._shorten(evidence, 155)}’. "
        if evidence_type == "inference":
            return (
                f"Your experience suggests exposure to {competency}, but the available "
                "evidence does not yet establish the exact scope or personal ownership. "
            )
        if evidence_type == "related":
            return (
                f"The CV contains related experience, but no direct evidence of {requirement or competency}. "
            )
        return (
            f"The CV provides limited detail about {requirement or competency}. "
        )

    def _is_verbatim_evidence(self, value: str) -> bool:
        clean = " ".join(str(value).split()).strip(" .:;,-")
        normalized = clean.casefold()
        if not clean or normalized in self._INTERNAL_EVIDENCE_LABELS:
            return False
        if len(clean.split()) < 5:
            return False
        if normalized.endswith(" scope") and len(clean.split()) <= 4:
            return False
        # A genuine CV line normally contains an action, context, result, or metric.
        return bool(
            re.search(r"\b(led|managed|delivered|implemented|designed|developed|owned|coordinated|improved|reduced|increased|supported|responsible|achieved|created|launched|transformed)\b", normalized)
            or re.search(r"\d", clean)
        )

    def _tokens(self, value: str) -> set[str]:
        return {
            token for token in re.findall(r"[a-z0-9]+", value.casefold())
            if len(token) > 3 and token not in {"management", "experience", "responsibility"}
        }

    def _concepts_overlap(self, left: str, right: str) -> bool:
        left_tokens = self._tokens(left)
        right_tokens = self._tokens(right)
        if left.casefold() == right.casefold():
            return True
        return bool(left_tokens and right_tokens and left_tokens.intersection(right_tokens))

    def _excerpt_around(self, value: str, phrase: str, limit: int = 220) -> str:
        clean = " ".join(str(value or "").split())
        if not phrase:
            return self._shorten(clean, limit)
        index = clean.casefold().find(phrase.casefold())
        if index < 0:
            return self._shorten(clean, limit)
        start = max(0, index - 70)
        end = min(len(clean), index + len(phrase) + 130)
        excerpt = clean[start:end].strip(" ,.;:-")
        if start > 0:
            excerpt = "…" + excerpt
        if end < len(clean):
            excerpt += "…"
        return excerpt

    def _shorten(self, value: str, limit: int) -> str:
        clean = " ".join(str(value).split())
        return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"
