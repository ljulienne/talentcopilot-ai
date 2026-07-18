"""Release 4.6 executive decision center.

The service interprets already-computed recruitment outputs. It never changes
Official Match, official rank, or canonical AI confidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ReadinessGap:
    label: str
    status: str
    rationale: str


@dataclass(frozen=True)
class EvidenceQualitySignal:
    label: str
    quality: str
    rationale: str


@dataclass(frozen=True)
class RampUpMilestone:
    period: str
    objective: str


@dataclass(frozen=True)
class CandidateComparisonSignal:
    candidate_name: str
    headline: str
    strengths: tuple[str, ...]
    trade_offs: tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveDecisionCenter:
    candidate_id: str
    candidate_name: str
    official_match_score: float
    official_rank: int
    ai_confidence: int
    decision_readiness: int
    readiness_label: str
    readiness_gaps: tuple[ReadinessGap, ...]
    evidence_quality: tuple[EvidenceQualitySignal, ...]
    confidence_reasons: tuple[str, ...]
    executive_summary: str
    hiring_risks: tuple
    interview_priorities: tuple[str, ...]
    timeline: tuple[RampUpMilestone, ...]
    recommendation: str
    recommended_action: str
    comparison: tuple[CandidateComparisonSignal, ...]
    governance_note: str


class ExecutiveDecisionCenterService:
    """Build a decision-readiness layer from canonical candidate outputs."""

    def build(self, report, intelligence, executive_brief, peer_reports: Sequence = ()) -> ExecutiveDecisionCenter:
        score = float(getattr(executive_brief, "official_match_score", 0.0) or 0.0)
        rank = int(getattr(executive_brief, "official_rank", 0) or 0)
        confidence = int(getattr(executive_brief, "ai_confidence", 0) or 0)
        gaps = self._readiness_gaps(report, intelligence)
        readiness = self._readiness_score(report, intelligence, confidence, gaps)
        evidence_quality = self._evidence_quality(report, intelligence)
        confidence_reasons = self._confidence_reasons(report, intelligence, confidence)
        timeline = self._timeline(executive_brief, gaps)
        comparison = self._comparison(report, peer_reports)
        summary = self._summary(
            getattr(executive_brief, "candidate_name", "Candidate"),
            score,
            confidence,
            readiness,
            gaps,
            evidence_quality,
            getattr(executive_brief, "recommendation", "Human validation required"),
        )
        return ExecutiveDecisionCenter(
            candidate_id=str(getattr(executive_brief, "candidate_id", "") or ""),
            candidate_name=str(getattr(executive_brief, "candidate_name", "Candidate") or "Candidate"),
            official_match_score=score,
            official_rank=rank,
            ai_confidence=confidence,
            decision_readiness=readiness,
            readiness_label=self._readiness_label(readiness),
            readiness_gaps=tuple(gaps),
            evidence_quality=tuple(evidence_quality),
            confidence_reasons=tuple(confidence_reasons),
            executive_summary=summary,
            hiring_risks=tuple(getattr(executive_brief, "risks", ()) or ()),
            interview_priorities=tuple(getattr(executive_brief, "interview_priorities", ()) or ()),
            timeline=tuple(timeline),
            recommendation=str(getattr(executive_brief, "recommendation", "Human validation required")),
            recommended_action=str(getattr(executive_brief, "recommended_action", "Complete human validation.")),
            comparison=tuple(comparison),
            governance_note=(
                "Decision readiness measures evidence completeness, not candidate quality. "
                "Official Match, rank and canonical AI confidence remain unchanged. "
                "A recruiter remains accountable for the final decision."
            ),
        )

    def _readiness_score(self, report, intelligence, confidence: int, gaps: Sequence[ReadinessGap]) -> int:
        evidence_coverage = self._bounded(getattr(intelligence, "evidence_coverage", 0))
        interview_count = len(tuple(getattr(intelligence, "interview_strategy", ()) or getattr(report, "interview_focus", ()) or ()))
        strengths_count = len(tuple(getattr(intelligence, "strengths", ()) or ()))
        penalty = sum(12 if gap.status == "Missing" else 6 for gap in gaps)
        raw = (evidence_coverage * 0.45) + (confidence * 0.35) + min(12, interview_count * 4) + min(8, strengths_count * 2) - penalty
        return self._bounded(round(raw))

    def _readiness_gaps(self, report, intelligence) -> list[ReadinessGap]:
        gaps: list[ReadinessGap] = []
        missing = self._unique(getattr(intelligence, "missing_evidence", ()) or ())
        for item in missing[:4]:
            gaps.append(ReadinessGap(item, "Missing", "The current structured evidence does not fully validate this requirement."))

        interview = tuple(getattr(intelligence, "interview_strategy", ()) or getattr(report, "interview_focus", ()) or ())
        if not interview:
            gaps.append(ReadinessGap("Structured interview plan", "Missing", "No role-specific validation plan is available yet."))

        evidence = tuple(getattr(report, "evidence", ()) or ())
        if not evidence:
            gaps.append(ReadinessGap("Documented evidence", "Missing", "No structured evidence item is available in the candidate report."))
        elif len(evidence) < 3:
            gaps.append(ReadinessGap("Evidence breadth", "Partial", "The recommendation relies on a limited number of structured evidence items."))

        risks = tuple(getattr(intelligence, "risks", ()) or ())
        if risks:
            gaps.append(ReadinessGap("Risk validation", "Partial", "At least one role-specific risk still requires recruiter validation."))
        return gaps[:6]

    def _evidence_quality(self, report, intelligence) -> list[EvidenceQualitySignal]:
        items = []
        for evidence in tuple(getattr(report, "evidence", ()) or ())[:6]:
            title = self._clean(getattr(evidence, "title", ""), "Candidate evidence")
            detail = self._clean(getattr(evidence, "detail", ""), "No detail available.")
            strength = self._clean(getattr(evidence, "strength", ""), "").lower()
            combined = f"{title} {detail}".lower()
            if any(token in combined for token in ("%", "increased", "reduced", "delivered", "led", "implemented", "managed")):
                quality = "Direct"
                rationale = "Specific ownership, delivery or measurable outcome is documented."
            elif strength in {"strong", "high"} or len(detail.split()) >= 8:
                quality = "Partial"
                rationale = "Relevant evidence exists, but scope or measurable outcomes should be confirmed."
            else:
                quality = "Weak inference"
                rationale = "The current signal is broad and requires direct validation."
            items.append(EvidenceQualitySignal(title, quality, rationale))

        if not items:
            summary = self._clean(getattr(intelligence, "evidence_summary", ""), "No structured evidence is available.")
            items.append(EvidenceQualitySignal("Evidence portfolio", "Weak inference", summary))
        return items

    def _confidence_reasons(self, report, intelligence, confidence: int) -> list[str]:
        reasons = []
        evidence = tuple(getattr(report, "evidence", ()) or ())
        skills = tuple(getattr(report, "skills", ()) or ())
        missing = tuple(getattr(intelligence, "missing_evidence", ()) or ())
        if len(evidence) >= 4:
            reasons.append("Multiple independent evidence items support the interpretation.")
        elif evidence:
            reasons.append("Some structured evidence is available, but breadth remains limited.")
        else:
            reasons.append("Confidence is constrained by the absence of structured evidence items.")
        if any(getattr(skill, "evidence", "") for skill in skills):
            reasons.append("Skill signals are linked to candidate evidence rather than labels alone.")
        if missing:
            reasons.append(f"Confidence is reduced by {len(missing)} unresolved evidence gap(s).")
        else:
            reasons.append("No material missing-evidence item is currently documented.")
        reasons.append(f"Canonical AI confidence supplied by the active session is {confidence}%.")
        return self._unique(reasons)[:4]

    def _timeline(self, executive_brief, gaps: Sequence[ReadinessGap]) -> list[RampUpMilestone]:
        immediate = "Confirm role scope, success criteria and the remaining evidence gaps."
        week_two = "Validate priority competencies through a structured interview and evidence-based scoring."
        month_one = "Complete onboarding objectives focused on the principal role-specific gap."
        month_three = "Demonstrate independent delivery against agreed outcomes and stakeholder expectations."
        month_six = "Review sustained performance, development priorities and longer-term contribution."
        if not gaps:
            immediate = "Confirm role objectives and convert the strong evidence base into an onboarding plan."
        return [
            RampUpMilestone("Week 1", immediate),
            RampUpMilestone("Week 2", week_two),
            RampUpMilestone("Month 1", month_one),
            RampUpMilestone("Month 3", month_three),
            RampUpMilestone("Month 6", month_six),
        ]

    def _comparison(self, selected_report, peer_reports: Sequence) -> list[CandidateComparisonSignal]:
        selected_score = float(getattr(selected_report, "official_match_score", None) or getattr(selected_report, "match_score", 0.0) or 0.0)
        selected_name = self._clean(getattr(selected_report, "candidate_name", ""), "Selected candidate")
        peers = [p for p in peer_reports or () if self._clean(getattr(p, "candidate_name", ""), "") != selected_name]
        peers.sort(key=lambda p: float(getattr(p, "official_match_score", None) or getattr(p, "match_score", 0.0) or 0.0), reverse=True)
        output = []
        for peer in peers[:2]:
            peer_name = self._clean(getattr(peer, "candidate_name", ""), "Peer candidate")
            peer_score = float(getattr(peer, "official_match_score", None) or getattr(peer, "match_score", 0.0) or 0.0)
            delta = selected_score - peer_score
            headline = f"{selected_name} is {abs(delta):.0f} point(s) {'ahead of' if delta >= 0 else 'behind'} {peer_name} on Official Match."
            selected_skills = self._top_skill_names(selected_report)
            peer_skills = self._top_skill_names(peer)
            strengths = [f"Stronger documented signal in {skill}." for skill in selected_skills if skill not in peer_skills][:2]
            trade_offs = [f"{peer_name} shows a stronger documented signal in {skill}." for skill in peer_skills if skill not in selected_skills][:2]
            if not strengths:
                strengths = ["No unique high-strength skill signal is documented versus this peer."]
            if not trade_offs:
                trade_offs = ["No material peer advantage is visible in the current structured skill evidence."]
            output.append(CandidateComparisonSignal(peer_name, headline, tuple(strengths), tuple(trade_offs)))
        return output

    def _top_skill_names(self, report) -> list[str]:
        values = []
        for skill in tuple(getattr(report, "skills", ()) or ()):
            if int(getattr(skill, "level", 0) or 0) >= 70:
                values.append(self._clean(getattr(skill, "name", ""), "Relevant capability"))
        return self._unique(values)

    def _summary(self, name, score, confidence, readiness, gaps, evidence_quality, recommendation) -> str:
        direct = sum(1 for item in evidence_quality if item.quality == "Direct")
        gap_text = gaps[0].label if gaps else "no material unresolved evidence gap"
        return (
            f"{name} has an Official Match of {score:.0f}% and canonical AI confidence of {confidence}%. "
            f"Decision readiness is {readiness}% with {direct} direct evidence signal(s). "
            f"Current recommendation: {recommendation}. The primary remaining validation point is {gap_text}."
        )

    def _readiness_label(self, value: int) -> str:
        if value >= 80:
            return "Decision-ready"
        if value >= 60:
            return "Ready with targeted validation"
        if value >= 40:
            return "Material evidence gaps"
        return "Insufficient decision evidence"

    def _bounded(self, value) -> int:
        try:
            return int(max(0, min(100, round(float(value or 0)))))
        except (TypeError, ValueError):
            return 0

    def _unique(self, values: Iterable[str]) -> list[str]:
        output = []
        seen = set()
        for value in values or ():
            clean = self._clean(value, "")
            key = clean.casefold()
            if clean and key not in seen:
                seen.add(key)
                output.append(clean)
        return output

    def _clean(self, value, fallback: str) -> str:
        text = " ".join(str(value or "").split())
        return text or fallback
