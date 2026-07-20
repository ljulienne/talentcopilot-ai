from __future__ import annotations

import json
import os
import pickle
import subprocess
import sys
from pathlib import Path

from talentcopilot.services.deterministic_scoring_contract import (
    SCORING_CONTRACT_VERSION,
    canonical_text,
    scoring_fingerprint,
)
from talentcopilot.services.upload_text_reader_service import UploadedTextDocument
from talentcopilot.ui.recruitment_upload_panel import _analysis_request_key


JOB_TEXT = """
Senior HRIS Project Manager. Minimum 10 years of HRIS project management.
SAP SuccessFactors and Power BI are essential. Lead system migrations,
interfaces, acceptance testing, data quality, change management and vendors.
Fluent English and French required.
"""

CANDIDATES = {
    "alpha.pdf": """
    Alpha Candidate. 12 years HRIS project management. SuccessFactors Employee
    Central, Power BI dashboards, interfaces, UAT, data quality, vendor and
    change management. Fluent French and English. Led an international team.
    """,
    "beta.pdf": """
    Beta Candidate. 11 years HRIS delivery. Workday, reporting, interfaces,
    testing, training and provider management. English and French.
    """,
    "gamma.pdf": """
    Gamma Candidate. Human Resources Director with Oracle HRIS exposure,
    transformation, coaching and workforce planning.
    """,
}


def _document(filename: str, text: str) -> UploadedTextDocument:
    return UploadedTextDocument(filename=filename, file_type="pdf", text=text, status="OK")


def _run_worker(tmp_path: Path, order: list[str], hash_seed: str) -> dict:
    payload = {
        "job_document": {
            "filename": "job.pdf",
            "file_type": "pdf",
            "text": JOB_TEXT,
            "status": "OK",
        },
        "candidate_documents": [
            {
                "filename": name,
                "file_type": "pdf",
                "text": CANDIDATES[name],
                "status": "OK",
            }
            for name in order
        ],
    }
    input_path = tmp_path / f"input-{hash_seed}-{'-'.join(order)}.json"
    output_path = tmp_path / f"output-{hash_seed}-{'-'.join(order)}.pkl"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = hash_seed
    env["TALENTCOPILOT_USE_LLM_EXTRACTION"] = "false"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "talentcopilot.services.isolated_recruitment_upload_worker",
            str(input_path),
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    with output_path.open("rb") as handle:
        session = pickle.load(handle)
    return {
        "session_id": session.session_id,
        "fingerprint": session.metadata["official_scoring_fingerprint"],
        "contract": session.metadata["canonical_score_contract"],
        "scores": [
            (
                analysis.candidate_name,
                analysis.match_score,
                analysis.rank,
                analysis.score_breakdown.get("decision_score"),
                analysis.score_breakdown.get("decision_rank"),
            )
            for analysis in session.ranked_analyses
        ],
    }


def test_scoring_fingerprint_ignores_candidate_order_and_whitespace():
    job = _document("job.pdf", JOB_TEXT)
    candidates = [_document(name, text) for name, text in CANDIDATES.items()]
    reverse = list(reversed(candidates))
    assert scoring_fingerprint(job_document=job, candidate_documents=candidates) == scoring_fingerprint(
        job_document=_document("job.pdf", "\r\n" + canonical_text(JOB_TEXT) + "\n"),
        candidate_documents=reverse,
    )


def test_worker_scores_are_exactly_repeatable_across_hash_seeds_and_upload_order(tmp_path):
    orders = [
        list(CANDIDATES),
        list(reversed(CANDIDATES)),
        ["beta.pdf", "gamma.pdf", "alpha.pdf"],
    ]
    results = [
        _run_worker(tmp_path, order, seed)
        for seed, order in zip(("1", "99", "8675309"), orders)
    ]
    assert results[0] == results[1] == results[2]
    assert results[0]["contract"] == SCORING_CONTRACT_VERSION


class _Upload:
    def __init__(self, value: bytes):
        self._value = value

    def getvalue(self):
        return self._value


def test_streamlit_request_key_ignores_candidate_upload_order():
    job = _Upload(b"job")
    candidates = [_Upload(b"a"), _Upload(b"b"), _Upload(b"c")]
    assert _analysis_request_key(job, candidates) == _analysis_request_key(job, list(reversed(candidates)))
