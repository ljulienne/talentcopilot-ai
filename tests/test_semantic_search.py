from talentcopilot.semantic.semantic_search import semantic_search


def test_semantic_search_workday():
    talents = [
        {
            "name": "Emma Martin",
            "talent_score": 95,
            "detected_skills": {
                "HRIS": ["Workday", "Power BI"],
            },
        },
        {
            "name": "John Smith",
            "talent_score": 88,
            "detected_skills": {
                "Payroll": ["SAP Payroll"],
            },
        },
    ]

    results = semantic_search(
        talents,
        "Workday",
    )

    assert len(results) == 1
    assert results[0]["talent"]["name"] == "Emma Martin"


def test_semantic_search_payroll():
    talents = [
        {
            "name": "Emma Martin",
            "talent_score": 95,
            "detected_skills": {
                "HRIS": ["Workday"],
            },
        },
        {
            "name": "John Smith",
            "talent_score": 88,
            "detected_skills": {
                "Payroll": ["Payroll", "SAP"],
            },
        },
    ]

    results = semantic_search(
        talents,
        "Payroll",
    )

    assert results[0]["talent"]["name"] == "John Smith"


def test_semantic_search_empty():
    assert semantic_search([], "Workday") == []


def test_semantic_search_no_query():
    talents = [{"name": "Emma"}]

    assert semantic_search(talents, "") == []
