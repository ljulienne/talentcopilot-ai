from talentcopilot.llm_extraction.real_matching import LLMRealMatchingInput, LLMRealMatchingPipeline
from talentcopilot.llm_extraction.real_ranking import LLMCandidateTextInput, LLMRealRankingInput, LLMRealRankingPipeline


def test_llm_real_matching_includes_hybrid_report(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")

    output = LLMRealMatchingPipeline().run(
        LLMRealMatchingInput(
            candidate_filename="vincent.txt",
            candidate_text="Vincent BLAKOE\n13 years experience HRIS Workday OCTIME Business Objects",
            job_filename="job.txt",
            job_text="HRIS Manager\nRequired skills: HRIS Time Management Reporting Project Management",
        )
    )

    assert output.hybrid_report is not None
    assert output.hybrid_report.semantic_score >= 0
    assert output.hybrid_report.explanation_report is not None


def test_llm_real_ranking_contains_hybrid_scores(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")

    output = LLMRealRankingPipeline().run(
        LLMRealRankingInput(
            job_filename="job.txt",
            job_text="HRIS Director. Required skills: HRIS Project Management Leadership.",
            candidates=[
                LLMCandidateTextInput("loretta.txt", "LORETTA DANIELSON, MBA, SPHR, SHRM-SCP\nHuman Resources Director"),
                LLMCandidateTextInput("vincent.txt", "Vincent BLAKOE\n13 years experience in HRIS consulting."),
            ],
        )
    )

    assert output.ranked_candidates
    assert all(candidate.hybrid_score >= 0 for candidate in output.ranked_candidates)
    assert all(candidate.matching_output.hybrid_report is not None for candidate in output.ranked_candidates)
