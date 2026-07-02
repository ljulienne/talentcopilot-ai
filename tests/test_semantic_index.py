from talentcopilot.semantic.semantic_index import (
    build_semantic_document,
    build_semantic_index,
)


def test_build_semantic_document():
    talent = {
        "name": "Emma Martin",
        "talent_score": 95,
        "average_score": 91,
        "highest_score": 97,
        "application_count": 2,
        "last_recruitment_title": "Global HRIS Manager",
        "detected_skills": {
            "HRIS": ["Workday", "SuccessFactors"],
            "Data": ["Power BI"],
        },
        "financial_data": {
            "expected_salary": 82000,
            "budget_max": 85000,
        },
        "application_history": [
            {
                "executive_summary": "Strong HRIS transformation profile."
            }
        ],
    }

    document = build_semantic_document(talent)

    assert "Emma Martin" in document
    assert "Workday" in document
    assert "Power BI" in document
    assert "82000" in document
    assert "Strong HRIS transformation profile." in document


def test_build_semantic_index():
    talents = [
        {
            "candidate_key": "emma",
            "name": "Emma Martin",
        }
    ]

    index = build_semantic_index(talents)

    assert len(index) == 1
    assert index[0]["candidate_key"] == "emma"
    assert index[0]["name"] == "Emma Martin"
    assert "document" in index[0]
