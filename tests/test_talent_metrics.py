from talentcopilot.talent_pool.talent_metrics import (
    calculate_talent_score,
    enrich_talent_profile,
    enrich_talent_profiles,
    get_best_application,
    get_latest_application,
    get_progression_trend,
)


def test_calculate_talent_score():
    talent = {
        "highest_score": 97,
        "average_score": 91,
        "average_confidence": 95,
    }

    assert calculate_talent_score(talent) == 94


def test_calculate_talent_score_with_empty_values():
    assert calculate_talent_score({}) == 0


def test_progression_trend_improving():
    talent = {
        "application_history": [
            {"score": 76, "updated_at": "2026-01-01T10:00:00"},
            {"score": 88, "updated_at": "2026-02-01T10:00:00"},
            {"score": 95, "updated_at": "2026-03-01T10:00:00"},
        ]
    }

    assert get_progression_trend(talent) == "Improving"


def test_progression_trend_declining():
    talent = {
        "application_history": [
            {"score": 92, "updated_at": "2026-01-01T10:00:00"},
            {"score": 80, "updated_at": "2026-02-01T10:00:00"},
        ]
    }

    assert get_progression_trend(talent) == "Declining"


def test_progression_trend_stable():
    talent = {
        "application_history": [
            {"score": 85, "updated_at": "2026-01-01T10:00:00"},
            {"score": 85, "updated_at": "2026-02-01T10:00:00"},
        ]
    }

    assert get_progression_trend(talent) == "Stable"


def test_progression_trend_not_enough_history():
    talent = {
        "application_history": [
            {"score": 85, "updated_at": "2026-01-01T10:00:00"},
        ]
    }

    assert get_progression_trend(talent) == "Not enough history"


def test_best_and_latest_application():
    talent = {
        "application_history": [
            {
                "recruitment_title": "HRIS Manager",
                "score": 88,
                "updated_at": "2026-01-01T10:00:00",
            },
            {
                "recruitment_title": "HRIS Product Owner",
                "score": 94,
                "updated_at": "2026-02-01T10:00:00",
            },
            {
                "recruitment_title": "Payroll Manager",
                "score": 82,
                "updated_at": "2026-03-01T10:00:00",
            },
        ]
    }

    assert get_best_application(talent)["recruitment_title"] == "HRIS Product Owner"
    assert get_latest_application(talent)["recruitment_title"] == "Payroll Manager"


def test_enrich_talent_profile():
    talent = {
        "name": "Emma Martin",
        "highest_score": 97,
        "average_score": 91,
        "average_confidence": 95,
        "application_history": [
            {"score": 88, "updated_at": "2026-01-01T10:00:00"},
            {"score": 97, "updated_at": "2026-02-01T10:00:00"},
        ],
    }

    enriched = enrich_talent_profile(talent)

    assert enriched["talent_score"] == 94
    assert enriched["progression_trend"] == "Improving"
    assert enriched["best_application"]["score"] == 97
    assert enriched["latest_application"]["score"] == 97


def test_enrich_talent_profiles_sorts_by_talent_score():
    talents = [
        {
            "name": "John Smith",
            "highest_score": 85,
            "average_score": 80,
            "average_confidence": 90,
        },
        {
            "name": "Emma Martin",
            "highest_score": 97,
            "average_score": 91,
            "average_confidence": 95,
        },
    ]

    enriched = enrich_talent_profiles(talents)

    assert enriched[0]["name"] == "Emma Martin"
    assert enriched[1]["name"] == "John Smith"
