from talentcopilot.llm_extraction.models import (
    CandidateExtractionResult,
    CandidateFacts,
    RoleExtractionResult,
    RoleFacts,
)


def test_candidate_extraction_model_validates_defaults():
    result = CandidateExtractionResult(facts=CandidateFacts(candidate_name="Loretta Danielson"))

    assert result.facts.candidate_name == "Loretta Danielson"
    assert result.facts.skills == []
    assert result.insights.missing_information == []


def test_role_extraction_model_validates_defaults():
    result = RoleExtractionResult(facts=RoleFacts(title="HRIS Director"))

    assert result.facts.title == "HRIS Director"
    assert result.facts.required_skills == []
    assert result.insights.critical_requirements == []
