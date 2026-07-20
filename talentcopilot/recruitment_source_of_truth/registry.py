from __future__ import annotations

from typing import Dict, Iterable, Optional

from .models import OfficialCandidateRecord, RecruitmentSourceOfTruth


class CandidateRegistry:
    def __init__(self, snapshot: RecruitmentSourceOfTruth):
        self._by_id: Dict[str, OfficialCandidateRecord] = {
            item.candidate_id: item for item in snapshot.candidates
        }
        self._by_name = {
            item.candidate_name.casefold(): item for item in snapshot.candidates
        }

    def get(self, candidate_key: str) -> Optional[OfficialCandidateRecord]:
        return self._by_id.get(candidate_key) or self._by_name.get(str(candidate_key).casefold())

    def all(self) -> Iterable[OfficialCandidateRecord]:
        return tuple(self._by_id.values())


class OfficialScoreRegistry(CandidateRegistry):
    def mission_fit(self, candidate_key: str) -> Optional[float]:
        record = self.get(candidate_key)
        return record.mission_fit_score if record else None

    def decision(self, candidate_key: str) -> Optional[float]:
        record = self.get(candidate_key)
        return record.decision_score if record else None


class OfficialRankingRegistry(CandidateRegistry):
    def mission_rank(self, candidate_key: str) -> Optional[int]:
        record = self.get(candidate_key)
        return record.mission_rank if record else None

    def decision_rank(self, candidate_key: str) -> Optional[int]:
        record = self.get(candidate_key)
        return record.decision_rank if record else None

    def interview_priority(self, candidate_key: str) -> Optional[int]:
        record = self.get(candidate_key)
        return record.interview_priority if record else None
