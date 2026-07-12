from __future__ import annotations

from typing import Any

from talentcopilot.models.mission import MissionCanvas, MissionDomain
from talentcopilot.models.mission_workspace import (
    MissionHealth,
    MissionJournalEntry,
    MissionWorkspaceSnapshot,
    NextBestAction,
)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _candidate_counts(session: Any | None) -> tuple[int, int]:
    if session is None:
        return 0, 0
    total = _safe_int(getattr(session, "candidate_count", 0))
    analysed = _safe_int(getattr(session, "analyzed_count", 0))
    if total == 0:
        candidates = getattr(session, "candidates", None)
        try:
            total = len(candidates) if candidates is not None else 0
        except TypeError:
            total = 0
    return total, analysed


def build_mission_workspace(canvas: MissionCanvas, session: Any | None = None) -> MissionWorkspaceSnapshot:
    """Build a transparent cockpit from current mission evidence.

    The scores describe decision preparedness, never the quality of a person.
    """
    required = tuple(canvas.required_inputs)
    total_candidates, analysed_candidates = _candidate_counts(session)

    readiness = 25
    confidence = {"High": 72, "Medium": 58, "Limited": 38}.get(canvas.confidence, 38)
    stage = "Mission understood"
    missing = list(required)
    reasons: list[str] = []
    actions: list[NextBestAction] = []
    journal = [
        MissionJournalEntry("Mission described", canvas.context),
        MissionJournalEntry("Mission routed", canvas.domain.value.replace("_", " ").title()),
        MissionJournalEntry("Workflow prepared", f"{len(canvas.recommended_workflow)} recommended steps"),
    ]

    if canvas.constraints:
        readiness += min(12, len(canvas.constraints) * 4)
        reasons.append("Business constraints have been detected.")

    if canvas.domain is MissionDomain.RECRUITMENT and session is not None:
        stage = "Recruitment evidence available"
        readiness += 20
        if missing:
            missing.pop(0)
        if total_candidates:
            readiness += 15
            if len(missing) > 1:
                missing.pop(1)
            journal.append(MissionJournalEntry("Candidate evidence available", f"{total_candidates} candidate(s) in the active recruitment"))
        if analysed_candidates:
            completion = min(1.0, analysed_candidates / max(total_candidates, 1))
            readiness += round(23 * completion)
            confidence += round(18 * completion)
            stage = "Candidate analysis in progress" if analysed_candidates < total_candidates else "Decision review"
            journal.append(MissionJournalEntry("Candidate analysis", f"{analysed_candidates}/{total_candidates} analysed"))
        reasons.append("The active recruitment provides real project evidence.")
    elif canvas.target_page:
        readiness += 8
        reasons.append("A compatible TalentCopilot workspace is already available.")
    else:
        reasons.append("The Studio is recognized but complete analytical evidence is not available yet.")

    readiness = max(0, min(100, readiness))
    confidence = max(0, min(100, confidence))

    for index, item in enumerate(missing[:3]):
        gain = max(4, 12 - index * 3)
        actions.append(
            NextBestAction(
                title=f"Provide {item.lower()}",
                reason="This evidence will reduce uncertainty and make the recommendation more defensible.",
                readiness_gain=gain,
                target_page=canvas.target_page,
            )
        )

    if not actions and canvas.target_page:
        actions.append(
            NextBestAction(
                title="Review the active decision workspace",
                reason="The available evidence is sufficient to continue with the detailed analysis.",
                readiness_gain=0,
                target_page=canvas.target_page,
            )
        )

    if readiness >= 78 and confidence >= 68:
        health = MissionHealth.STRONG
    elif readiness >= 48:
        health = MissionHealth.NEEDS_ATTENTION
    else:
        health = MissionHealth.AT_RISK

    if missing:
        reasons.append(f"{len(missing)} evidence area(s) still need validation.")
    else:
        reasons.append("No core evidence category is currently marked as missing.")

    reasoning = (
        "Mission readiness reflects the business context, detected constraints and evidence currently available. "
        "Decision confidence reflects how safely TalentCopilot can support a human decision. Neither score evaluates a person."
    )

    return MissionWorkspaceSnapshot(
        mission_title=canvas.mission_title,
        domain_label=canvas.domain.value.replace("_", " ").title(),
        stage=stage,
        readiness=readiness,
        decision_confidence=confidence,
        health=health,
        health_reasons=tuple(reasons),
        missing_evidence=tuple(missing),
        next_actions=tuple(actions),
        journal=tuple(journal),
        reasoning=reasoning,
    )
