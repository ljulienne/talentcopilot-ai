from __future__ import annotations

import re
from typing import Iterable

from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.models.candidate_workspace import (
    CandidateEvidence,
    CandidateRisk,
    CandidateSkill,
    CandidateWorkspaceReport,
)
from talentcopilot.services.candidate_identity import resolve_candidate_id
from talentcopilot.recruitment_reasoning import UniversalCandidateRiskGroundingEngine


class CandidateWorkspaceService:
    """Build one coherent Candidate Intelligence report per candidate.

    Release 7.2.0 enriches presentation-level intelligence only. The official
    match score and official rank remain immutable and are read from the active
    RecruitmentSession source of truth.
    """

    def __init__(self, risk_engine=None):
        self.risk_engine = risk_engine or UniversalCandidateRiskGroundingEngine()

    def build_all(self, session=None):
        if session is None or not getattr(session, "ranked_analyses", None):
            return []

        candidates_by_id = {}
        candidates_by_name = {}
        for candidate in getattr(session, "candidates", []) or []:
            candidate_id = resolve_candidate_id(candidate)
            candidates_by_id[candidate_id] = candidate
            name = candidate.get("name")
            if name:
                candidates_by_name.setdefault(name, candidate)

        job = dict(getattr(session, "job", {}) or {})
        reports = []
        ordered_analyses = RecruitmentSourceOfTruthService().ordered_analyses(session)
        for official_rank, analysis in enumerate(ordered_analyses, start=1):
            candidate = candidates_by_id.get(getattr(analysis, "candidate_id", ""))
            if candidate is None:
                candidate = candidates_by_name.get(analysis.candidate_name, {})
            report = self._build_one(analysis, candidate, job)
            # The source-of-truth order is the canonical candidate order. Align
            # the presentation rank with that order without changing any score,
            # decision score or persisted analysis output.
            report.rank = official_rank
            report.score_breakdown["mission_fit_rank"] = official_rank
            reports.append(report)
        return reports

    def _build_one(self, analysis, candidate, job=None):
        job = dict(job or {})
        decision_report = getattr(analysis, "decision_report", None)
        recommendation = "Human review required"
        executive_summary = "No decision summary available yet."

        if decision_report:
            recommendation = getattr(
                getattr(decision_report, "recommendation", None),
                "value",
                getattr(decision_report, "recommendation", recommendation),
            )
            executive_summary = getattr(
                decision_report,
                "executive_summary",
                executive_summary,
            )

        required_skills = self._job_requirements(job)
        candidate_skills = self._unique(candidate.get("skills", []) or [])
        achievements = self._unique(candidate.get("achievements", []) or [])
        candidate_text = self._candidate_text(candidate)

        skills = self._build_skills(
            required_skills=required_skills,
            candidate_skills=candidate_skills,
            achievements=achievements,
            candidate_text=candidate_text,
        )
        evidence = self._build_evidence(
            skills=skills,
            achievements=achievements,
            candidate_text=candidate_text,
        )
        risks = self._build_risks(
            decision_report=decision_report,
            skills=skills,
            achievements=achievements,
            candidate_text=candidate_text,
            candidate=candidate,
            job=job,
        )
        interview_focus = self._build_interview_focus(
            decision_report=decision_report,
            risks=risks,
            skills=skills,
            achievements=achievements,
        )

        score = float(
            getattr(
                analysis,
                "official_match_score",
                getattr(analysis, "match_score", 0.0),
            )
            or 0.0
        )
        recommendation_label = self._recommendation_label(
            str(recommendation),
            score,
            risks,
        )
        recommendation_rationale = self._recommendation_rationale(
            candidate_name=getattr(analysis, "candidate_name", "Candidate"),
            label=recommendation_label,
            skills=skills,
            risks=risks,
        )
        next_action = self._next_action(recommendation_label, risks, skills)

        return CandidateWorkspaceReport(
            candidate_name=getattr(analysis, "candidate_name", "Candidate"),
            candidate_id=getattr(analysis, "candidate_id", "") or resolve_candidate_id(candidate),
            rank=int(
                (getattr(analysis, "score_breakdown", {}) or {}).get("mission_fit_rank")
                or getattr(analysis, "rank", None)
                or getattr(analysis, "official_rank", 0)
                or 0
            ),
            match_score=score,
            score_breakdown=dict(getattr(analysis, "score_breakdown", {}) or {}),
            recommendation=str(recommendation),
            executive_summary=str(executive_summary),
            skills=skills,
            evidence=evidence,
            risks=risks,
            interview_focus=interview_focus,
            recommendation_label=recommendation_label,
            recommendation_rationale=recommendation_rationale,
            next_action=next_action,
        )

    def _job_requirements(self, job):
        """Return role requirements from every supported job representation.

        Upload sessions frequently carry a richer domain-agnostic technical
        requirement catalog than the legacy ``required_skills`` list. Using both
        prevents risk grounding from collapsing to a generic fallback when a job
        description does not contain a literal "Skills" section.
        """

        values = list(
            job.get("required_skills")
            or job.get("skills")
            or job.get("competencies")
            or []
        )
        technical = list(job.get("technical_requirements") or [])
        priority = {"critical": 0, "high": 1, "supporting": 2, "preferred": 3}
        technical.sort(
            key=lambda item: (
                priority.get(str((item or {}).get("importance", "high")).casefold(), 2),
                -float((item or {}).get("required_level", 0) or 0),
                str((item or {}).get("name", "")).casefold(),
            )
            if isinstance(item, dict)
            else (2, 0, str(item).casefold())
        )
        for item in technical:
            name = item.get("name") if isinstance(item, dict) else str(item)
            if name:
                values.append(name)
        return self._unique(values)[:12]

    def _build_skills(self, *, required_skills, candidate_skills, achievements, candidate_text):
        ordered = self._unique([*required_skills, *candidate_skills])[:12]
        required_keys = {self._normalise(value) for value in required_skills}
        achievement_text = " ".join(achievements)
        skills = []

        for index, name in enumerate(ordered):
            key = self._normalise(name)
            explicit = any(self._equivalent(name, item) for item in candidate_skills)
            mentions = self._mention_count(name, candidate_text)
            achievement_mentions = self._mention_count(name, achievement_text)
            ownership = self._contains_any(
                candidate_text,
                ("led", "managed", "owned", "directed", "responsible", "pilot", "dirig", "gér", "responsable"),
            )
            measurable = bool(re.search(r"\b\d+(?:[.,]\d+)?\s*(?:%|users?|countries?|sites?|projects?|million|m\b)", candidate_text, re.I))

            level = 24
            if explicit:
                level += 38
            level += min(18, mentions * 6)
            level += min(12, achievement_mentions * 6)
            if ownership and (explicit or mentions):
                level += 6
            if measurable and achievement_mentions:
                level += 5
            if key not in required_keys:
                level -= 6
            level = max(15, min(95, level))

            evidence = self._best_evidence(name, achievements)
            if not evidence and explicit:
                evidence = f"Explicitly listed in the candidate profile: {name}."
            elif not evidence:
                evidence = f"No direct evidence of {name} was identified in the current CV data."

            if level >= 80:
                status, confidence = "Strong evidence", "High"
            elif level >= 60:
                status, confidence = "Moderate evidence", "Moderate"
            elif level >= 40:
                status, confidence = "Limited evidence", "Limited"
            else:
                status, confidence = "Not demonstrated", "Low"

            skills.append(CandidateSkill(
                name=str(name),
                level=level,
                evidence=evidence,
                status=status,
                confidence=confidence,
                requirement_type="Role requirement" if key in required_keys else "Additional capability",
            ))

        return sorted(skills, key=lambda item: (item.requirement_type != "Role requirement", -item.level, item.name.lower()))

    def _build_evidence(self, *, skills, achievements, candidate_text):
        items = []
        for skill in skills[:8]:
            direct = skill.status in {"Strong evidence", "Moderate evidence"}
            evidence_text = self._best_evidence(skill.name, achievements) or skill.evidence
            ownership = self._ownership_label(evidence_text)
            outcome = self._outcome_label(evidence_text)
            items.append(CandidateEvidence(
                title=skill.name,
                detail=evidence_text,
                strength="High" if skill.level >= 80 else "Medium" if skill.level >= 55 else "Low",
                requirement=skill.requirement_type,
                source="Candidate CV / structured extraction",
                ownership=ownership,
                outcome=outcome,
                confidence=skill.confidence,
                evidence_type="Direct evidence" if direct else "Evidence gap / indirect signal",
            ))

        for achievement in achievements:
            if any(achievement == item.detail for item in items):
                continue
            items.append(CandidateEvidence(
                title="Additional achievement",
                detail=achievement,
                strength="High" if self._outcome_label(achievement) != "Not quantified" else "Medium",
                requirement="Supporting evidence",
                source="Candidate CV",
                ownership=self._ownership_label(achievement),
                outcome=self._outcome_label(achievement),
                confidence="High" if len(achievement.split()) >= 6 else "Moderate",
                evidence_type="Direct evidence",
            ))
            if len(items) >= 10:
                break

        if not items:
            items.append(CandidateEvidence(
                title="Evidence availability",
                detail="The current profile contains insufficient structured evidence for a detailed assessment.",
                strength="Low",
                requirement="Decision readiness",
                confidence="Low",
                evidence_type="Evidence gap",
            ))
        return items

    def _build_risks(
        self,
        *,
        decision_report,
        skills,
        achievements,
        candidate_text,
        candidate=None,
        job=None,
    ):
        """Build universal, candidate-grounded decision risks.

        This delegates to a domain-agnostic engine. The engine may reference any
        requirement found in the active job, but never hard-codes a job family,
        industry or technology and never changes the official score or rank.
        """

        return self.risk_engine.build(
            decision_report=decision_report,
            skills=skills,
            candidate=candidate or {},
            job=job or {},
            achievements=achievements,
            candidate_text=candidate_text,
            limit=3,
        )

    def _build_interview_focus(self, *, decision_report, risks, skills, achievements):
        focus = []
        for item in getattr(decision_report, "interview_focus", []) or []:
            text = str(item).strip()
            if text:
                focus.append(text)

        for risk in risks:
            focus.append(f"Priority validation — {risk.related_requirement}: {risk.interview_question}")

        strong = [skill for skill in skills if skill.level >= 70][:2]
        for skill in strong:
            focus.append(
                f"Evidence depth — {skill.name}: Ask for one recent example, personal decisions, stakeholders, trade-offs and measurable outcome."
            )

        if achievements:
            focus.append(
                f"Achievement verification — Explore the scope and individual contribution behind: {achievements[0]}"
            )

        focus.extend([
            "Positive signals — precise ownership, credible scope, measurable outcomes and clear trade-off reasoning.",
            "Warning signals — vague collective language, unverified tool exposure or inability to separate personal contribution from team delivery.",
        ])
        return self._unique(focus)[:8]

    def _recommendation_label(self, recommendation, score, risks):
        text = recommendation.lower()
        high_risks = sum(1 for risk in risks if risk.severity.lower() == "high")
        if "reject" in text or "not recommend" in text or (score < 35 and high_risks):
            return "Do not prioritize"
        if score >= 70 and not high_risks:
            return "Proceed"
        if score >= 45:
            return "Proceed with validation"
        return "Hold for further evidence"

    def _recommendation_rationale(self, *, candidate_name, label, skills, risks):
        strengths = [skill.name for skill in skills if skill.level >= 70][:2]
        strength_text = " and ".join(strengths) if strengths else "the available role-relevant evidence"
        if risks:
            reserve = risks[0].related_requirement or risks[0].title
            return f"{candidate_name} is assessed as {label.lower()}, supported by {strength_text}. The principal decision uncertainty concerns {reserve}."
        return f"{candidate_name} is assessed as {label.lower()}, supported by {strength_text}. No material candidate-specific risk is currently established from the available evidence."

    def _next_action(self, label, risks, skills):
        if label == "Do not prioritize":
            return "Retain only if additional evidence materially changes the current assessment."
        if risks:
            return f"Run a structured interview focused first on {risks[0].related_requirement or risks[0].title}."
        top = skills[0].name if skills else "the strongest role requirement"
        return f"Advance to structured interview and verify {top} through a recent, measurable example."

    def _best_evidence(self, skill, achievements):
        ranked = sorted(
            achievements,
            key=lambda item: (self._mention_count(skill, item), len(str(item))),
            reverse=True,
        )
        if ranked and self._mention_count(skill, ranked[0]) > 0:
            return str(ranked[0])
        return ""

    def _ownership_label(self, text):
        if self._contains_any(text, ("led", "managed", "owned", "directed", "responsible", "pilot", "dirig", "gér", "responsable")):
            return "Direct ownership indicated"
        if self._contains_any(text, ("supported", "contributed", "assisted", "participated", "collaborated")):
            return "Contributory role indicated"
        return "Ownership not established"

    def _outcome_label(self, text):
        match = re.search(r"\b\d+(?:[.,]\d+)?\s*(?:%|users?|countries?|sites?|projects?|million|m\b)", str(text), re.I)
        return match.group(0) if match else "Not quantified"

    def _candidate_text(self, candidate):
        values = []
        for key in ("title", "summary", "skills", "achievements", "experience", "experiences", "responsibilities", "technologies"):
            value = candidate.get(key)
            if isinstance(value, (list, tuple)):
                values.extend(str(item) for item in value)
            elif value:
                values.append(str(value))
        return " ".join(values)

    def _mention_count(self, term, text):
        tokens = [token for token in re.findall(r"[a-z0-9]+", self._normalise(term)) if len(token) > 2]
        haystack = self._normalise(text)
        if not tokens:
            return 0
        return sum(1 for token in tokens if re.search(rf"\b{re.escape(token)}\b", haystack))

    def _equivalent(self, left, right):
        a, b = self._normalise(left), self._normalise(right)
        if not a or not b:
            return False
        return a == b or a in b or b in a

    def _normalise(self, value):
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(value).lower())).strip()

    def _contains_any(self, text, values):
        lower = str(text).lower()
        return any(value.lower() in lower for value in values)

    def _unique(self, values: Iterable):
        output, seen = [], set()
        for value in values or []:
            text = str(value).strip()
            key = self._normalise(text)
            if text and key not in seen:
                seen.add(key)
                output.append(text)
        return output

    def _dedupe_risks(self, risks):
        output, seen = [], set()
        for risk in risks:
            key = self._normalise(f"{risk.title} {risk.related_requirement}")
            if key not in seen:
                seen.add(key)
                output.append(risk)
        return output
