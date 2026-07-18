"""Executive Decision Intelligence built from canonical candidate outputs.

This service is presentation and decision-support only. It never recalculates
Official Match, official rank, or the canonical AI confidence signal.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class HiringRiskDimension:
    name: str
    level: str
    rationale: str


@dataclass(frozen=True)
class ExecutiveDecisionBrief:
    candidate_id: str
    candidate_name: str
    official_match_score: float
    official_rank: int
    ai_confidence: int
    recommendation: str
    decision_label: str
    business_impact: str
    executive_summary: str
    why: Tuple[str, ...]
    risks: Tuple[HiringRiskDimension, ...]
    interview_priorities: Tuple[str, ...]
    recommended_action: str
    expected_ramp_up: str
    ramp_up_rationale: str
    evidence_summary: str

    @property
    def decision_status(self) -> str:
        return self.decision_label

    @property
    def next_action(self) -> str:
        return self.recommended_action

    @property
    def ramp_up(self) -> str:
        return self.expected_ramp_up

    @property
    def executive_narrative(self) -> str:
        return self.executive_summary

    @property
    def strengths(self) -> Tuple[str, ...]:
        return self.why

    @property
    def governance_note(self) -> str:
        return (
            "Decision support only. Official Match and rank come directly from "
            "the active recruitment session. A recruiter remains accountable "
            "for the final decision."
        )


class _DecisionBriefReportAdapter:
    def __init__(self, brief):
        self.candidate_id = getattr(brief, "candidate_id", "")
        self.candidate_name = getattr(brief, "candidate_name", "Candidate")
        self.official_match_score = getattr(brief, "official_match_score", 0.0)
        self.official_rank = getattr(brief, "official_rank", 0)
        self.score_breakdown = {"confidence": getattr(brief, "confidence_score", 0)}
        self.skills = []
        self.interview_focus = tuple(getattr(brief, "interview_priorities", ()) or ())


class _DecisionBriefIntelligenceAdapter:
    def __init__(self, brief):
        self.decision_confidence = getattr(brief, "confidence_score", 0)
        self.strengths = tuple(getattr(brief, "strengths", ()) or ())
        self.missing_evidence = tuple(getattr(brief, "missing_evidence", ()) or ())
        self.interview_strategy = tuple(getattr(brief, "interview_priorities", ()) or ())
        self.evidence_summary = getattr(brief, "evidence_summary", "")
        self.risks = tuple(getattr(brief, "hiring_risks", ()) or ())


class ExecutiveDecisionIntelligenceService:
    """Create a deterministic executive brief from existing structured outputs."""

    def build(self, report, intelligence=None) -> ExecutiveDecisionBrief:
        # Release 4.5A supports both the legacy (report, intelligence) contract
        # and the canonical CandidateDecisionBrief contract used by the UI.
        if intelligence is None:
            brief = report
            report = _DecisionBriefReportAdapter(brief)
            intelligence = _DecisionBriefIntelligenceAdapter(brief)

        score = float(getattr(report, 'official_match_score', None) or getattr(report, 'match_score', 0.0) or 0.0)
        rank = int(getattr(report, 'official_rank', None) or getattr(report, 'rank', 0) or 0)
        confidence = self._confidence(report, intelligence)
        strengths = self._unique(getattr(intelligence, 'strengths', ()) or self._skill_names(report, 75))[:4]
        missing = self._unique(getattr(intelligence, 'missing_evidence', ()))[:4]
        interview = self._unique(getattr(intelligence, 'interview_strategy', ()) or getattr(report, 'interview_focus', ()))[:3]
        risks = self._risk_matrix(report, intelligence, score, confidence, missing)
        recommendation, label, action = self._decision(score, confidence)
        ramp_up, ramp_rationale = self._ramp_up(score, confidence, missing)
        why = strengths or ('No role-specific strength has been evidenced yet.',)
        summary = self._summary(report, score, confidence, recommendation, why, risks)
        return ExecutiveDecisionBrief(
            candidate_id=self._clean(getattr(report, 'candidate_id', ''), ''),
            candidate_name=self._clean(getattr(report, 'candidate_name', ''), 'Candidate'),
            official_match_score=score,
            official_rank=rank,
            ai_confidence=confidence,
            recommendation=recommendation,
            decision_label=label,
            business_impact=self._business_impact(score, confidence),
            executive_summary=summary,
            why=tuple(why),
            risks=tuple(risks),
            interview_priorities=tuple(interview or ('Validate scope, ownership and measurable outcomes.',)),
            recommended_action=action,
            expected_ramp_up=ramp_up,
            ramp_up_rationale=ramp_rationale,
            evidence_summary=self._clean(getattr(intelligence, 'evidence_summary', ''), 'Evidence summary is not available.'),
        )

    def _confidence(self, report, intelligence) -> int:
        value = dict(getattr(report, 'score_breakdown', {}) or {}).get('confidence')
        if value is None:
            value = getattr(intelligence, 'decision_confidence', 0)
        try:
            return int(max(0, min(100, round(float(value)))))
        except (TypeError, ValueError):
            return 0

    def _decision(self, score, confidence):
        if confidence < 50:
            return ('Manual review required', 'LOW CONFIDENCE', 'Complete a recruiter-led evidence review before progressing.')
        if score >= 80:
            return ('Strong Hire', 'STRONG HIRE', 'Invite to a structured final interview.')
        if score >= 60:
            return ('Hire with targeted validation', 'HIRE WITH VALIDATION', 'Invite to interview and validate the priority gaps.')
        if score >= 40:
            return ('Consider for adjacent fit', 'CONSIDER', 'Review transferable fit before deciding on interview progression.')
        return ('Do not prioritize', 'MATERIAL GAPS', 'Do not progress unless the role scope or talent pool criteria change.')

    def _risk_matrix(self, report, intelligence, score, confidence, missing):
        risk_items = list(getattr(intelligence, 'risks', ()) or [])
        skills_level = 'Low' if not missing and score >= 70 else ('Medium' if score >= 50 else 'High')
        experience_level = 'Low' if score >= 75 else ('Medium' if score >= 45 else 'High')
        evidence_level = 'Low' if confidence >= 80 else ('Medium' if confidence >= 60 else 'High')
        output = [
            HiringRiskDimension('Skills', skills_level, ('No material skill gap is documented.' if not missing else 'Limited or missing evidence for ' + ', '.join(missing[:2]) + '.')),
            HiringRiskDimension('Experience', experience_level, 'Validate the scale, ownership and outcomes of the most relevant assignments.'),
            HiringRiskDimension('Evidence quality', evidence_level, f'Canonical AI confidence is {confidence}%.'),
        ]
        if risk_items:
            first = risk_items[0]
            if isinstance(first, str):
                rationale = self._clean(first, 'Role-specific evidence requires validation.')
            else:
                rationale = self._clean(
                    getattr(first, 'detail', ''),
                    self._clean(getattr(first, 'title', ''), 'Role-specific evidence requires validation.'),
                )
            output.append(HiringRiskDimension('Role-specific', 'Medium', rationale))
        return output

    def _ramp_up(self, score, confidence, missing):
        if score >= 80 and confidence >= 75 and not missing:
            return 'Immediate to 1 month', 'Strong role alignment and well-supported evidence indicate limited onboarding friction.'
        if score >= 65 and confidence >= 60:
            return '1–2 months', 'Core capabilities are present; targeted onboarding should address the remaining validation points.'
        if score >= 40:
            return '2–3 months', 'Transferable capabilities may support the role, but material gaps require structured onboarding.'
        return 'Long ramp-up', 'Current role alignment is limited and several core requirements need development or validation.'

    def _business_impact(self, score, confidence):
        if score >= 80 and confidence >= 70: return 'High'
        if score >= 55 and confidence >= 55: return 'Moderate'
        return 'Limited'

    def _summary(self, report, score, confidence, recommendation, why, risks):
        name = self._clean(getattr(report, 'candidate_name', ''), 'Candidate')
        risk = next((r.rationale for r in risks if r.level in {'High','Medium'}), 'No material risk is documented.')
        return f'{name} has an official match of {score:.0f}% and canonical AI confidence of {confidence}%. {recommendation}. Primary supporting signal: {why[0]} Main validation point: {risk}'

    def _skill_names(self, report, minimum):
        return [self._clean(getattr(s, 'name', ''), '') for s in getattr(report, 'skills', []) or [] if int(getattr(s, 'level', 0) or 0) >= minimum]

    def _unique(self, values: Iterable[str]):
        out=[]; seen=set()
        for value in values or []:
            clean=self._clean(value,''); key=clean.casefold()
            if clean and key not in seen: out.append(clean); seen.add(key)
        return out

    def _clean(self, value, fallback):
        text=' '.join(str(value or '').split())
        return text or fallback
