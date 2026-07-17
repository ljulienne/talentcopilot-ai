
from pathlib import Path

from talentcopilot.document_intelligence.candidate_extractor import (
    CandidateDocumentExtractor,
)
from talentcopilot.document_intelligence.pipeline import (
    DocumentIntelligencePipeline,
)
from talentcopilot.job_intelligence.pipeline import (
    JobIntelligencePipeline,
)
from talentcopilot.job_intelligence.role_extractor import (
    RoleProfileExtractor,
)


def test_candidate_deterministic_mode_ignores_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "fake-key",
    )
    monkeypatch.setenv(
        "TALENTCOPILOT_USE_LLM_EXTRACTION",
        "true",
    )

    extractor = CandidateDocumentExtractor(
        extraction_mode=(
            CandidateDocumentExtractor.DETERMINISTIC_MODE
        )
    )

    assert extractor._should_use_llm() is False


def test_role_deterministic_mode_ignores_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "fake-key",
    )
    monkeypatch.setenv(
        "TALENTCOPILOT_USE_LLM_EXTRACTION",
        "true",
    )

    extractor = RoleProfileExtractor(
        extraction_mode=(
            RoleProfileExtractor.DETERMINISTIC_MODE
        )
    )

    assert extractor._should_use_llm() is False


def test_document_pipeline_propagates_candidate_mode():
    pipeline = DocumentIntelligencePipeline(
        extraction_mode=(
            CandidateDocumentExtractor.DETERMINISTIC_MODE
        )
    )

    assert (
        pipeline.extractor.extraction_mode
        == CandidateDocumentExtractor.DETERMINISTIC_MODE
    )


def test_job_pipeline_propagates_role_mode():
    pipeline = JobIntelligencePipeline(
        extraction_mode=(
            RoleProfileExtractor.DETERMINISTIC_MODE
        )
    )

    assert (
        pipeline.extractor.extraction_mode
        == RoleProfileExtractor.DETERMINISTIC_MODE
    )


def test_official_matching_uses_deterministic_modes():
    source = Path(
        "talentcopilot/real_matching/pipeline.py"
    ).read_text(encoding="utf-8")

    assert (
        "CandidateDocumentExtractor.DETERMINISTIC_MODE"
        in source
    )

    assert (
        "RoleProfileExtractor.DETERMINISTIC_MODE"
        in source
    )
