from __future__ import annotations

import hashlib
import json
from typing import Any, List

from .cache import RecruitmentAnalysisCache
from .contracts import assert_snapshot_matches_session
from .models import OfficialCandidateRecord, RecruitmentSourceOfTruth
from .registry import CandidateRegistry, OfficialRankingRegistry, OfficialScoreRegistry


class RecruitmentSourceOfTruthService:
    VERSION = "recruitment-sot-v1.0"
    METADATA_KEY = "recruitment_source_of_truth"

    def freeze(self, session: Any, *, replace: bool = False) -> RecruitmentSourceOfTruth:
        existing = self._from_metadata(session)
        if existing is not None and not replace:
            assert_snapshot_matches_session(existing, session)
            return RecruitmentAnalysisCache.put(existing)

        analyses = list(getattr(session, "analyses", []) or [])
        mission_order = sorted(
            analyses,
            key=lambda item: (
                -float(getattr(item, "match_score", 0) or 0),
                str(getattr(item, "candidate_name", "")).casefold(),
                str(getattr(item, "candidate_id", "")),
            ),
        )
        mission_ranks = {
            str(getattr(item, "candidate_id", "")): index
            for index, item in enumerate(mission_order, start=1)
        }

        records: List[OfficialCandidateRecord] = []
        for position, analysis in enumerate(
            sorted(analyses, key=lambda item: int(getattr(item, "rank", 9999) or 9999)),
            start=1,
        ):
            candidate_id = str(getattr(analysis, "candidate_id", ""))
            decision_rank = int(getattr(analysis, "rank", position) or position)
            records.append(
                OfficialCandidateRecord(
                    candidate_id=candidate_id,
                    candidate_name=str(getattr(analysis, "candidate_name", "Candidate")),
                    mission_fit_score=round(float(getattr(analysis, "match_score", 0) or 0), 2),
                    decision_score=self._optional_float(getattr(analysis, "decision_score", None)),
                    mission_rank=mission_ranks.get(candidate_id, position),
                    decision_rank=decision_rank,
                    interview_priority=decision_rank,
                    confidence=self._optional_float(getattr(analysis, "official_confidence_score", None)),
                    score_breakdown=dict(getattr(analysis, "score_breakdown", {}) or {}),
                )
            )

        fingerprint = self._fingerprint(records)
        snapshot = RecruitmentSourceOfTruth(
            session_id=str(getattr(session, "session_id", "session")),
            role_title=str(getattr(session, "role_title", "Recruitment")),
            version=self.VERSION,
            candidates=records,
            analysis_fingerprint=fingerprint,
        )
        metadata = getattr(session, "metadata", None)
        if metadata is None:
            session.metadata = {}
            metadata = session.metadata
        metadata[self.METADATA_KEY] = snapshot.to_dict()
        metadata["official_analysis_fingerprint"] = fingerprint
        metadata["official_analysis_version"] = self.VERSION
        return RecruitmentAnalysisCache.put(snapshot)

    def get(self, session: Any, *, validate: bool = True) -> RecruitmentSourceOfTruth:
        session_id = str(getattr(session, "session_id", "session"))
        snapshot = RecruitmentAnalysisCache.get(session_id) or self._from_metadata(session)
        if snapshot is None:
            snapshot = self.freeze(session)
        if validate:
            assert_snapshot_matches_session(snapshot, session)
        return RecruitmentAnalysisCache.put(snapshot)

    def registries(self, session: Any):
        snapshot = self.get(session)
        return {
            "candidates": CandidateRegistry(snapshot),
            "scores": OfficialScoreRegistry(snapshot),
            "rankings": OfficialRankingRegistry(snapshot),
        }

    def ordered_analyses(self, session: Any):
        snapshot = self.get(session)
        by_id = {
            str(getattr(item, "candidate_id", "")): item
            for item in getattr(session, "analyses", [])
        }
        return [by_id[item.candidate_id] for item in sorted(snapshot.candidates, key=lambda x: x.decision_rank)]

    def _from_metadata(self, session: Any):
        payload = (getattr(session, "metadata", {}) or {}).get(self.METADATA_KEY)
        if not payload:
            return None
        return RecruitmentSourceOfTruth.from_dict(payload)

    def _fingerprint(self, records: List[OfficialCandidateRecord]) -> str:
        payload = json.dumps([item.to_dict() for item in records], sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _optional_float(self, value):
        if value is None:
            return None
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return None
