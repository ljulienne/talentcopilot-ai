from talentcopilot.semantic.lexical_search import LexicalSearchEngine


def test_lexical_search_engine_returns_results():
    talents = [
        {
            "name": "Emma Martin",
            "talent_score": 95,
            "detected_skills": {"HRIS": ["Workday"]},
        },
        {
            "name": "John Smith",
            "talent_score": 80,
            "detected_skills": {"Payroll": ["Payroll"]},
        },
    ]

    engine = LexicalSearchEngine()
    results = engine.search(talents, "Workday")

    assert len(results) == 1
    assert results[0]["talent"]["name"] == "Emma Martin"
