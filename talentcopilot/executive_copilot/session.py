from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .models import CopilotResponse


@dataclass(frozen=True)
class CopilotHistoryEntry:
    question_id: str
    question_title: str
    summary: str
    confidence: float
    created_at: datetime


def history_entry(response: CopilotResponse) -> CopilotHistoryEntry:
    return CopilotHistoryEntry(
        question_id=response.question.question_id,
        question_title=response.question.title,
        summary=response.answer.summary,
        confidence=response.answer.confidence,
        created_at=datetime.now(timezone.utc),
    )
