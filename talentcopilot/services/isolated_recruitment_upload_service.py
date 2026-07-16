"""Canonical upload analysis executed outside Streamlit state."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List
import json
import os
import pickle
import subprocess
import sys

from talentcopilot.models.recruitment_session import (
    RecruitmentSession,
)
from talentcopilot.services.upload_text_reader_service import (
    UploadedTextDocument,
)


class IsolatedRecruitmentUploadService:
    """Run the official upload pipeline in a clean Python process."""

    def __init__(self, timeout_seconds: int = 300):
        self.timeout_seconds = timeout_seconds

    def run(
        self,
        job_document: UploadedTextDocument,
        candidate_documents: List[UploadedTextDocument],
    ) -> RecruitmentSession:
        payload = {
            "job_document": self._serialize(job_document),
            "candidate_documents": [
                self._serialize(document)
                for document in candidate_documents
            ],
        }

        repo_path = Path(__file__).resolve().parents[2]
        worker_module = (
            "talentcopilot.services."
            "isolated_recruitment_upload_worker"
        )

        with TemporaryDirectory(
            prefix="talentcopilot-isolated-"
        ) as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "input.json"
            output_path = temp_path / "output.pkl"

            input_path.write_text(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            environment = os.environ.copy()
            current_pythonpath = environment.get(
                "PYTHONPATH",
                "",
            )

            environment["PYTHONPATH"] = os.pathsep.join(
                item
                for item in [
                    str(repo_path),
                    current_pythonpath,
                ]
                if item
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    worker_module,
                    str(input_path),
                    str(output_path),
                ],
                cwd=str(repo_path),
                env=environment,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
            )

            if result.returncode != 0:
                details = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "Unknown isolated worker error"
                )
                raise RuntimeError(
                    "Canonical isolated scoring failed: "
                    + details
                )

            if not output_path.exists():
                raise RuntimeError(
                    "The isolated scoring worker produced "
                    "no RecruitmentSession."
                )

            with output_path.open("rb") as output_file:
                session = pickle.load(output_file)

        if not isinstance(session, RecruitmentSession):
            raise TypeError(
                "The isolated worker returned an unexpected "
                f"object: {type(session)!r}"
            )

        return session

    def _serialize(
        self,
        document: UploadedTextDocument,
    ) -> dict:
        return {
            "filename": str(document.filename),
            "file_type": str(document.file_type),
            "text": str(document.text or ""),
            "status": str(document.status or "OK"),
        }
