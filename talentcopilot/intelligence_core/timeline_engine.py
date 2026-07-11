from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from .models import (
    DecisionEvent,
    DecisionProgress,
    DecisionQueue,
    DecisionStatus,
    DecisionTimeline,
)


_ALLOWED_TRANSITIONS = {
    DecisionStatus.PROPOSED: {
        DecisionStatus.ACCEPTED,
        DecisionStatus.DISMISSED,
    },
    DecisionStatus.ACCEPTED: {
        DecisionStatus.IN_PROGRESS,
        DecisionStatus.DISMISSED,
    },
    DecisionStatus.IN_PROGRESS: {
        DecisionStatus.COMPLETED,
        DecisionStatus.ACCEPTED,
        DecisionStatus.DISMISSED,
    },
    DecisionStatus.COMPLETED: set(),
    DecisionStatus.DISMISSED: {
        DecisionStatus.PROPOSED,
    },
}


class DecisionTimelineEngine:
    """Tracks human validation and execution of AI-proposed decisions."""

    def initialize(
        self,
        queue: DecisionQueue,
        *,
        occurred_at: str | None = None,
    ) -> DecisionTimeline:
        timestamp = occurred_at or self._now()
        items = []
        for decision in queue.decisions:
            event = DecisionEvent(
                event_id=f"{decision.decision_id}-event-1",
                decision_id=decision.decision_id,
                status=decision.status,
                occurred_at=timestamp,
                note="Decision proposed from organizational evidence.",
                actor="TalentCopilot",
            )
            items.append(DecisionProgress(decision=decision, events=(event,)))
        return DecisionTimeline(items=tuple(items))

    def transition(
        self,
        timeline: DecisionTimeline,
        *,
        decision_id: str,
        status: DecisionStatus | str,
        note: str = "",
        actor: str = "TalentCopilot user",
        occurred_at: str | None = None,
    ) -> DecisionTimeline:
        target_status = status if isinstance(status, DecisionStatus) else DecisionStatus(status)
        updated_items = []
        found = False

        for item in timeline.items:
            if item.decision.decision_id != decision_id:
                updated_items.append(item)
                continue

            found = True
            current = item.current_status
            if target_status == current:
                updated_items.append(item)
                continue
            if target_status not in _ALLOWED_TRANSITIONS[current]:
                raise ValueError(
                    f"Invalid decision transition: {current.value} -> {target_status.value}."
                )

            event = DecisionEvent(
                event_id=f"{decision_id}-event-{len(item.events) + 1}",
                decision_id=decision_id,
                status=target_status,
                occurred_at=occurred_at or self._now(),
                note=note.strip(),
                actor=actor.strip() or "TalentCopilot user",
            )
            updated_items.append(replace(item, events=(*item.events, event)))

        if not found:
            raise KeyError(f"Unknown decision_id: {decision_id}")
        return DecisionTimeline(items=tuple(updated_items))

    @staticmethod
    def allowed_next_statuses(status: DecisionStatus) -> tuple[DecisionStatus, ...]:
        return tuple(sorted(_ALLOWED_TRANSITIONS[status], key=lambda item: item.value))

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
