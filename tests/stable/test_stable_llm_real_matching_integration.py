from talentcopilot.llm_extraction.real_matching import LLMRealMatchingInput, LLMRealMatchingPipeline


def test_llm_real_matching_pipeline_mock_candidate_name(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")

    output = LLMRealMatchingPipeline().run(
        LLMRealMatchingInput(
            candidate_filename="loretta.txt",
            candidate_text="LORETTA DANIELSON, MBA, SPHR, SHRM-SCP\nHuman Resources Director",
            job_filename="job.txt",
            job_text="HRIS Director\nRequired skills: HRIS, Project Management",
        )
    )

    assert output.candidate_extraction.facts.candidate_name == "Loretta Danielson"
    assert output.decision_output.profile.candidate_name == "Loretta Danielson"


def test_llm_real_matching_pipeline_vincent_mock(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")

    output = LLMRealMatchingPipeline().run(
        LLMRealMatchingInput(
            candidate_filename="vincent.txt",
            candidate_text="Vincent BLAKOE\n13 years experience in HRIS consulting.",
            job_filename="job.txt",
            job_text="HRIS Project Manager\nRequired skills: HRIS, Project Management",
        )
    )

    assert output.candidate_extraction.facts.candidate_name == "Vincent Blakoe"
