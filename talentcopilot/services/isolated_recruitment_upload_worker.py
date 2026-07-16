"""Execute canonical recruitment scoring in an isolated process."""

from __future__ import annotations

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
    candidate_documents = [
        _document(item)
        for item in payload["candidate_documents"]
    ]

    session = RecruitmentUploadSessionService().run(
        job_document,
        candidate_documents,
    )

    metadata = dict(getattr(session, "metadata", {}) or {})
    metadata.update(
        {
            "execution_mode": "isolated_subprocess",
            "canonical_score_contract": "fit-score-v1",
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
