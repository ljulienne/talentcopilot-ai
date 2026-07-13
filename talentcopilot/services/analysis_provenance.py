"""Analysis provenance and compatibility rules.

This module intentionally uses explicit product versions rather than Git as the
runtime source of truth. Streamlit Cloud may not expose a full Git checkout, but
every RecruitmentSession must still declare which official pipeline created it.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping, Optional


ANALYSIS_SCHEMA_VERSION = "3.2.1A.2.2"
MATCHING_ENGINE_VERSION = "real-ranking-v1"
NORMALIZATION_VERSION = "3.1.1C"
OFFICIAL_PIPELINE = "real-upload-ranking"


@dataclass(frozen=True)
class AnalysisProvenance:
    analysis_version: str
    pipeline: str
    matching_engine_version: str
    normalization_version: str
    job_document_hash: str
    candidate_document_hashes: tuple[str, ...]
    created_at: str

    def as_metadata(self) -> dict:
        return {
            "analysis_version": self.analysis_version,
            "pipeline": self.pipeline,
            "matching_engine_version": self.matching_engine_version,
            "normalization_version": self.normalization_version,
            "job_document_hash": self.job_document_hash,
            "candidate_document_hashes": list(
                self.candidate_document_hashes
            ),
            "analysis_created_at": self.created_at,
        }


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(bytes(value or b"")).hexdigest()


def hash_text(value: str) -> str:
    return hashlib.sha256(
        str(value or "").encode("utf-8")
    ).hexdigest()


def build_provenance(
    job_text: str,
    candidate_texts: Iterable[str],
) -> AnalysisProvenance:
    return AnalysisProvenance(
        analysis_version=ANALYSIS_SCHEMA_VERSION,
        pipeline=OFFICIAL_PIPELINE,
        matching_engine_version=MATCHING_ENGINE_VERSION,
        normalization_version=NORMALIZATION_VERSION,
        job_document_hash=hash_text(job_text),
        candidate_document_hashes=tuple(
            hash_text(text)
            for text in candidate_texts
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def session_compatibility_reason(session) -> Optional[str]:
    """Return None when a session is current, otherwise a user-safe reason.

    Demo sessions are not rejected because they are presentation fixtures rather
    than persisted real-upload analyses. Real-upload sessions must declare the
    complete current provenance contract.
    """

    if session is None:
        return None

    metadata = dict(getattr(session, "metadata", {}) or {})
    source = str(metadata.get("source", "") or "")

    if source != "real_upload":
        return None

    expected = {
        "analysis_version": ANALYSIS_SCHEMA_VERSION,
        "pipeline": OFFICIAL_PIPELINE,
        "matching_engine_version": MATCHING_ENGINE_VERSION,
        "normalization_version": NORMALIZATION_VERSION,
    }

    for field, value in expected.items():
        actual = str(metadata.get(field, "") or "")
        if actual != value:
            return (
                "This recruitment analysis was produced by an older or "
                "different analysis pipeline. Run the analysis again to "
                "refresh its official scores."
            )

    if not metadata.get("job_document_hash"):
        return (
            "This recruitment analysis has no job-document provenance. "
            "Run the analysis again to refresh its official scores."
        )

    candidate_hashes = metadata.get("candidate_document_hashes")
    if not isinstance(candidate_hashes, (list, tuple)) or not candidate_hashes:
        return (
            "This recruitment analysis has no candidate-document provenance. "
            "Run the analysis again to refresh its official scores."
        )

    return None


def is_session_compatible(session) -> bool:
    return session_compatibility_reason(session) is None
