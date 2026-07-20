"""Deterministic identity for the canonical recruitment scoring pipeline.

The contract deliberately excludes timestamps, session state and candidate upload
order. Identical extracted job/CV text under the same engine versions must create
one stable fingerprint and therefore one stable official score set.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Sequence


SCORING_CONTRACT_VERSION = "deterministic-recruitment-scoring-v7.0.1"
PYTHON_HASH_SEED = "0"


def canonical_text(value: str) -> str:
    """Return a platform-independent text representation for hashing.

    Matching still receives the original extracted text. This function only
    creates deterministic identities and does not alter evidence evaluation.
    """

    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return "\n".join(line for line in lines if line).strip()


def text_hash(value: str) -> str:
    return hashlib.sha256(canonical_text(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ScoringDocumentIdentity:
    filename: str
    text_hash: str

    def to_dict(self) -> dict[str, str]:
        return {"filename": self.filename, "text_hash": self.text_hash}


def document_identity(document) -> ScoringDocumentIdentity:
    return ScoringDocumentIdentity(
        filename=str(getattr(document, "filename", "") or ""),
        text_hash=text_hash(str(getattr(document, "text", "") or "")),
    )


def canonical_candidate_identities(documents: Iterable) -> tuple[ScoringDocumentIdentity, ...]:
    identities = [document_identity(document) for document in documents]
    return tuple(sorted(identities, key=lambda item: (item.text_hash, item.filename.casefold())))


def scoring_fingerprint(
    *,
    job_document,
    candidate_documents: Sequence,
    engine_versions: Iterable[str] = (),
) -> str:
    payload = {
        "contract": SCORING_CONTRACT_VERSION,
        "job": document_identity(job_document).to_dict(),
        "candidates": [
            item.to_dict()
            for item in canonical_candidate_identities(candidate_documents)
        ],
        "engines": sorted(str(value) for value in engine_versions if str(value)),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def canonicalize_candidate_documents(documents: Iterable) -> list:
    """Sort candidate documents by content identity before running the pipeline."""

    return sorted(
        list(documents),
        key=lambda document: (
            text_hash(str(getattr(document, "text", "") or "")),
            str(getattr(document, "filename", "") or "").casefold(),
        ),
    )
