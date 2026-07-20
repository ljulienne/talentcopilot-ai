

"""Execute canonical recruitment scoring in an isolated process."""

from __future__ import annotations
import os

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pathlib import Path
import json
import pickle
import sys

from talentcopilot.services.recruitment_upload_session_service import (
    RecruitmentUploadSessionService,
)
from talentcopilot.services.upload_text_reader_service import (
    UploadedTextDocument,
)
from talentcopilot.services.deterministic_scoring_contract import (
    SCORING_CONTRACT_VERSION,
    canonicalize_candidate_documents,
    scoring_fingerprint,
)
from talentcopilot.recruitment_reasoning import RecruitmentReasoningEngine
from talentcopilot.calibrated_scoring import CalibratedMissionScoringEngine
from talentcopilot.comparative_ranking import ComparativeRankingEngine
from talentcopilot.career_intelligence import CareerFitEngine
from talentcopilot.decision_ranking import DecisionRankingPolicy

# Official Match must remain independent from runtime LLM secrets.
os.environ["TALENTCOPILOT_USE_LLM_EXTRACTION"] = "false"
os.environ.pop("OPENAI_API_KEY", None)



def _document(data: dict) -> UploadedTextDocument:
    return UploadedTextDocument(
        filename=str(data["filename"]),
        file_type=str(data["file_type"]),
        text=str(data["text"]),
        status=str(data.get("status") or "OK"),
    )


def main() -> int:
    if len(sys.argv) != 3:
        raise RuntimeError(
            "Usage: isolated_recruitment_upload_worker "
            "<input.json> <output.pkl>"
        )

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    payload = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    job_document = _document(payload["job_document"])
    candidate_documents = canonicalize_candidate_documents(
        _document(item)
        for item in payload["candidate_documents"]
    )

    engine_versions = (
        RecruitmentReasoningEngine.version,
        CalibratedMissionScoringEngine.version,
        ComparativeRankingEngine.version,
        CareerFitEngine.version,
        DecisionRankingPolicy.version,
    )
    fingerprint = scoring_fingerprint(
        job_document=job_document,
        candidate_documents=candidate_documents,
        engine_versions=engine_versions,
    )

    session = RecruitmentUploadSessionService().run(
        job_document,
        candidate_documents,
    )

    metadata = dict(getattr(session, "metadata", {}) or {})
    metadata.update(
        {
            "execution_mode": "isolated_subprocess",
            "canonical_score_contract": SCORING_CONTRACT_VERSION,
            "official_scoring_fingerprint": fingerprint,
            "official_scoring_engine_versions": list(engine_versions),
            "official_scoring_hash_seed": os.environ.get("PYTHONHASHSEED", ""),
        }
    )
    session.metadata = metadata

    with output_path.open("wb") as output_file:
        pickle.dump(
            session,
            output_file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
