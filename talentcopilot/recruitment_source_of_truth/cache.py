from __future__ import annotations

from typing import Dict, Optional

from .models import RecruitmentSourceOfTruth


class RecruitmentAnalysisCache:
    """Process-local cache. The serializable snapshot also lives in session.metadata."""

    _cache: Dict[str, RecruitmentSourceOfTruth] = {}

    @classmethod
    def get(cls, session_id: str) -> Optional[RecruitmentSourceOfTruth]:
        return cls._cache.get(session_id)

    @classmethod
    def put(cls, snapshot: RecruitmentSourceOfTruth) -> RecruitmentSourceOfTruth:
        cls._cache[snapshot.session_id] = snapshot
        return snapshot

    @classmethod
    def invalidate(cls, session_id: str) -> None:
        cls._cache.pop(session_id, None)
