from __future__ import annotations

from typing import Iterable, Optional
import re

from talentcopilot.interview.models import InterviewCompetency, InterviewQuestion


class InterviewQuestionService:
    """Build varied evidence-grounded questions without an LLM call."""

    ENGINE_VERSION = "7.2.1-evidence-grounding"
    REQUIREMENT_ENGINE_VERSION = "7.7.0-domain-agnostic-requirement-intelligence"

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
        elif declared_status == "Ambiguous evidence":
            evidence_type = "inference"
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
            requirement_kind=str(getattr(competency, "requirement_kind", "") or ""),
            requirement_family=str(getattr(competency, "requirement_family", "") or ""),
            components=list(getattr(competency, "components", []) or []),
            importance=str(getattr(competency, "importance", "") or ""),
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
        requirement_kind: str = "",
        requirement_family: str = "",
        components: list[str] | None = None,
        importance: str = "",
    ):
        """Build a question from evidence status and requirement type.

        The templates are domain-agnostic. Product-specific depth is supplied
        by the extracted family/context rather than by a role-specific question
        catalogue.
        """
        prefix = self._evidence_prefix(
            competency=competency,
            requirement=requirement,
            evidence=evidence,
            evidence_type=evidence_type,
        )
        related = ", ".join((related_evidence or [])[:4])
        family = (requirement_family or "").casefold()
        kind = (requirement_kind or "").casefold()
        component_label = ", ".join((components or [])[:4]) or competency
        critical_note = " This is a critical role requirement." if importance == "Critical" else ""

        if "artificial intelligence" in family or kind == "technical_innovation":
            return (
                prefix + critical_note +
                f" Describe the most relevant applied AI or automation initiative you personally delivered for {role_title}. "
                "Clarify the use case, data, model or service used, your own contribution, validation method, measurable outcome, "
                "privacy controls, bias and explainability risks, and where human oversight remained necessary. "
                "If you have not deployed such a solution, propose a realistic first use case and explain how you would govern it.",
                [
                    "A real use case or a credible implementation approach",
                    "Personal technical or functional ownership",
                    "Data quality, privacy, bias and explainability controls",
                    "Measurable business outcome and human oversight",
                ],
                [
                    "Separates experimentation from production deployment",
                    "Explains model or service selection and validation",
                    "Recognises bias, privacy and human-decision risks",
                ],
                [
                    "Uses AI terminology without a concrete use case",
                    "Cannot explain data, validation or governance",
                    "Treats automated output as a decision without human control",
                ],
                [
                    "Which failure mode or bias would you test first?",
                    "How would you measure value without overstating causality?",
                    "Which decisions must remain under human oversight?",
                ],
            )

        if kind in {"technical_platform", "technical_tool"} and evidence_type in {"gap", "related"}:
            transfer = f" The CV shows related experience with {related}." if related else ""
            return (
                prefix + transfer + critical_note +
                f" The role requires {component_label}. Describe any direct experience that may be absent from the CV. "
                "If your experience is with adjacent products or technologies, explain what is genuinely transferable, "
                "the important product-specific differences, the learning curve, and how you would de-risk delivery in the first 90 days.",
                [
                    "Exact products, versions, modules or components used",
                    "Personal configuration, design or delivery responsibility",
                    "A precise comparison with the related technology",
                    "A credible learning and risk-mitigation plan",
                ],
                [
                    "Distinguishes direct expertise from transferable experience",
                    "Names concrete product-specific differences",
                    "Connects prior evidence to the target delivery context",
                ],
                [
                    "Treats all tools in the family as interchangeable",
                    "Cannot describe hands-on ownership",
                    "Offers no credible transfer or upskilling plan",
                ],
                [
                    "Which feature or component would create the steepest learning curve?",
                    "Which prior design decision would not transfer safely?",
                    "What proof would demonstrate readiness before production delivery?",
                ],
            )

        if kind in {"technical_platform", "technical_tool"}:
            bi_depth = (
                " Include the semantic model, transformations, calculation logic or formulas (such as DAX when applicable), refresh, security and reconciliation controls."
                if "business intelligence" in family else ""
            )
            database_depth = (
                " Include schema design, query or performance decisions, availability, security and migration considerations."
                if "database" in family else ""
            )
            engineering_depth = (
                " Include architecture, interfaces, testing, deployment, observability and non-functional trade-offs."
                if any(value in family for value in ("software", "cloud", "devops", "cyber")) else ""
            )
            return (
                prefix + critical_note +
                f" Describe the most advanced solution you personally delivered using {component_label}. "
                "What did you configure, design, build or operate, at what scale, with which dependencies and controls, and what measurable decision or outcome changed?"
                + bi_depth + database_depth + engineering_depth,
                [
                    "Exact scope, version, modules or technical components",
                    "Personal hands-on ownership",
                    "Architecture, data, integration, security or testing decisions",
                    "Scale, adoption and measurable outcome",
                ],
                [
                    "Explains concrete technical or functional decisions",
                    "Separates personal contribution from team activity",
                    "Connects implementation choices to an outcome",
                ],
                [
                    "Mentions the tool only as a user or project label",
                    "Cannot explain design, configuration or validation",
                    "No objective measure of success",
                ],
                [
                    "Which product-specific feature was most difficult?",
                    "How did you validate the result against the source or expected behaviour?",
                    "What would you redesign today and why?",
                ],
            )

        if kind == "certification":
            return (
                prefix + critical_note +
                f" The role references {component_label}. Confirm the certification, its current validity and level, "
                "then describe a work situation where you applied the underlying standard or body of knowledge to make a decision or improve an outcome.",
                ["Certification issuer and validity", "Applied knowledge", "Personal decision or deliverable", "Outcome"],
                ["Provides verifiable credential detail", "Connects certification knowledge to practice"],
                ["Credential cannot be verified", "No evidence of practical application"],
                ["Which part of the standard do you use most often?", "How do you keep the knowledge current?", "What result improved because of it?"],
            )

        if kind == "methodology":
            return (
                prefix + critical_note +
                f" Describe a situation where you applied {component_label} rather than merely naming the method. "
                "Why was it appropriate, what practices did you personally use, what trade-offs did you make, and what measurable result followed?",
                ["Context and method selection", "Practices personally applied", "Trade-offs", "Measured result"],
                ["Adapts the method to context", "Names concrete practices and artefacts"],
                ["Uses methodology vocabulary without applied evidence", "Cannot explain trade-offs"],
                ["Which practice had the greatest impact?", "What did you deliberately not apply?", "How did you measure effectiveness?"],
            )

        if archetype == "data":
            return (
                prefix + critical_note +
                f" Describe a {competency} deliverable that influenced a business decision. "
                "Which sources, definitions, controls and analytical choices did you personally own, and what measurable action or outcome followed?",
                ["Data sources", "Definitions and validation", "Personal analytical ownership", "Decision impact"],
                ["Explains lineage and validation", "Connects analysis to a decision"],
                ["Cannot explain source quality", "No decision or outcome"],
                ["Which assumption was most sensitive?", "How did you reconcile conflicting sources?", "Who acted on the result?"],
            )

        if archetype == "change":
            return (
                prefix + critical_note +
                f" Choose one transformation where adoption of {competency} was uncertain. "
                "What resistance did you diagnose, which communication, training or process interventions did you personally lead, and how was adoption measured?",
                ["Stakeholder resistance", "Personal intervention", "Adoption measure", "Sustained outcome"],
                ["Uses evidence to adapt the change plan", "Measures adoption beyond attendance"],
                ["Describes communication only", "No adoption evidence"],
                ["Which group resisted most?", "What did you change after feedback?", "How did you know adoption was sustained?"],
            )

        if archetype in {"leadership", "stakeholder"}:
            return (
                prefix + critical_note +
                f" Describe the most complex situation in which you personally led {competency}. "
                "Who had conflicting objectives, what decision or governance mechanism did you own, and what measurable outcome followed?",
                ["Stakeholder map", "Personal decision authority", "Conflict or trade-off", "Outcome"],
                ["Shows clear ownership and influence", "Explains governance and trade-offs"],
                ["Relies only on collective language", "Cannot identify a decision personally owned"],
                ["Who disagreed and why?", "What did you decide personally?", "Which metric proves the outcome?"],
            )

        if archetype == "risk":
            return (
                prefix + critical_note +
                f" Describe the highest-risk situation you encountered in {competency}. "
                "How did you identify and quantify the risk, which control or corrective action did you personally implement, and what residual risk remained?",
                ["Risk identification", "Control ownership", "Evidence of effectiveness", "Residual risk"],
                ["Quantifies risk and control effectiveness", "Acknowledges residual risk"],
                ["Offers generic assurance", "No evidence that controls worked"],
                ["What was the earliest warning signal?", "Which control failed first?", "Who accepted the residual risk?"],
            )

        return (
            prefix + critical_note +
            f" Describe one example that best proves your personal contribution to {competency}. "
            "What responsibility did you personally own, what did you deliver, which constraints or trade-offs did you manage, and which measurable result assessed success?",
            ["Personal accountability", "Concrete deliverable", "Trade-offs", "Measured result"],
            ["Shows clear ownership", "Separates personal contribution from team activity", "Uses evidence to demonstrate impact"],
            ["Uses only collective language", "Cannot identify a personal deliverable", "No objective success measure"],
            ["What would not have happened without your contribution?", "Who can verify the result?", "Which outcome is most directly attributable to your work?"],
        )

    def _archetype(self, competency: str, index: int) -> str:
        value = competency.lower()
        if any(token in value for token in ("analytics", "report", "data", "dashboard", "forecast", "consolidation")):
            return "data"
        if any(token in value for token in ("change", "adoption", "training", "transformation")):
            return "change"
        if any(token in value for token in ("stakeholder", "vendor", "supplier", "committee", "communication", "account")):
            return "stakeholder"
        if any(token in value for token in ("management", "leadership", "coaching", "team", "sales")):
            return "leadership"
        if any(token in value for token in ("risk", "quality", "compliance", "governance", "safety", "control")):
            return "risk"
        if any(token in value for token in ("system", "platform", "software", "database", "cloud", "interface", "integration", "testing", "engineering", "architecture")):
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
        clean = competency.casefold()
        phrases = [clean]
        for part in re.split(r"\s+(?:&|and|for)\s+|/", clean):
            part = part.strip()
            if len(part) >= 3:
                phrases.append(part)
        compact = re.sub(r"[^a-z0-9+#]", "", clean)
        if compact:
            phrases.append(compact)
        return tuple(dict.fromkeys(phrases))

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
