from types import SimpleNamespace

from talentcopilot.services.analysis_provenance import (
    ANALYSIS_SCHEMA_VERSION,
    MATCHING_ENGINE_VERSION,
    NORMALIZATION_VERSION,
    OFFICIAL_PIPELINE,
    build_provenance,
    session_compatibility_reason,
)
from talentcopilot.services.recruitment_upload_session_service import (
    RecruitmentUploadSessionService,
)
from talentcopilot.services.upload_text_reader_service import (
    UploadedTextDocument,
)


def test_provenance_is_deterministic_for_identical_documents():
    first = build_provenance(
        "job text",
        ["candidate one", "candidate two"],
    )
    second = build_provenance(
        "job text",
        ["candidate one", "candidate two"],
    )

    assert first.job_document_hash == second.job_document_hash
    assert (
        first.candidate_document_hashes
        == second.candidate_document_hashes
    )
    assert first.pipeline == OFFICIAL_PIPELINE


def test_old_real_upload_session_is_rejected():
    session = SimpleNamespace(
        metadata={
            "source": "real_upload",
            "workflow_version": "3.1.1A",
        }
    )

    reason = session_compatibility_reason(session)

    assert reason
    assert "older or different analysis pipeline" in reason


def test_current_real_upload_session_is_compatible():
    session = SimpleNamespace(
        metadata={
            "source": "real_upload",
            "analysis_version": ANALYSIS_SCHEMA_VERSION,
            "pipeline": OFFICIAL_PIPELINE,
            "matching_engine_version": MATCHING_ENGINE_VERSION,
            "normalization_version": NORMALIZATION_VERSION,
            "job_document_hash": "job-hash",
            "candidate_document_hashes": ["candidate-hash"],
        }
    )

    assert session_compatibility_reason(session) is None


def test_demo_session_is_not_invalidated():
    session = SimpleNamespace(
        metadata={"source": "demo"}
    )

    assert session_compatibility_reason(session) is None


def test_real_upload_session_contains_provenance():
    class RankingService:
        def run(self, job_document, candidate_documents):
            profile = SimpleNamespace(
                role_title="HRIS Project Manager",
                evidence_graph=SimpleNamespace(
                    nodes=[],
                    sources=[],
                ),
            )
            ranked = SimpleNamespace(
                candidate_name="Louis Julienne",
                candidate_filename="Louis.pdf",
                fit_score=86,
                ranking_score=77,
                rank=1,
                recommendation="Proceed",
                rationale="Strong evidence.",
                matching_output=SimpleNamespace(
                    decision_output=SimpleNamespace(
                        profile=profile,
                    )
                ),
            )
            return SimpleNamespace(
                status="Ready",
                job_document=job_document,
                candidate_documents=candidate_documents,
                ranking_output=SimpleNamespace(
                    role_title="HRIS Project Manager",
                    ranked_candidates=[ranked],
                ),
            )

    service = RecruitmentUploadSessionService(
        ranking_service=RankingService()
    )
    session = service.run(
        UploadedTextDocument(
            "job.txt",
            "txt",
            "HRIS Project Manager",
        ),
        [
            UploadedTextDocument(
                "Louis.pdf",
                "pdf",
                "Louis Julienne\n10 years HRIS",
            )
        ],
    )

    assert session.metadata["analysis_version"] == ANALYSIS_SCHEMA_VERSION
    assert session.metadata["pipeline"] == OFFICIAL_PIPELINE
    assert session.metadata["job_document_hash"]
    assert len(session.metadata["candidate_document_hashes"]) == 1
    assert session.ranked_analyses[0].match_score == 86
