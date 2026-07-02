from talentcopilot.talent_pool import talent_store as store
from talentcopilot.talent_pool.talent_profile import (
    build_talent_profile_from_result,
    index_recruitment_talents,
)


def test_build_talent_profile_from_single_application(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "TALENT_POOL_DIR", tmp_path / "talent_pool")
    monkeypatch.setattr(store, "TALENT_INDEX_PATH", tmp_path / "talent_pool" / "talents.json")

    recruitment = {
        "id": "REC-001",
        "title": "HRIS Project Manager",
        "updated_at": "2026-07-02T10:00:00",
    }

    result = {
        "candidate": {"name": "Emma Martin"},
        "match_result": {
            "overall_score": 92,
            "confidence_score": 95,
            "recommendation": "Strong Hire",
            "executive_summary": "Strong HRIS profile.",
        },
    }

    profile = build_talent_profile_from_result(recruitment, result)

    assert profile["candidate_key"] == "emma-martin"
    assert profile["name"] == "Emma Martin"
    assert profile["application_count"] == 1
    assert profile["average_score"] == 92
    assert profile["highest_score"] == 92
    assert profile["average_confidence"] == 95
    assert profile["last_recruitment_title"] == "HRIS Project Manager"


def test_talent_profile_merges_application_history(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "TALENT_POOL_DIR", tmp_path / "talent_pool")
    monkeypatch.setattr(store, "TALENT_INDEX_PATH", tmp_path / "talent_pool" / "talents.json")

    first_recruitment = {
        "id": "REC-001",
        "title": "HRIS Project Manager",
        "updated_at": "2026-07-02T10:00:00",
    }

    second_recruitment = {
        "id": "REC-002",
        "title": "HRIS Product Owner",
        "updated_at": "2026-07-03T10:00:00",
    }

    first_result = {
        "candidate": {"name": "Emma Martin"},
        "match_result": {
            "overall_score": 80,
            "confidence_score": 90,
        },
    }

    second_result = {
        "candidate": {"name": "Emma Martin"},
        "match_result": {
            "overall_score": 94,
            "confidence_score": 96,
        },
    }

    build_talent_profile_from_result(first_recruitment, first_result)
    profile = build_talent_profile_from_result(second_recruitment, second_result)

    assert profile["application_count"] == 2
    assert profile["average_score"] == 87
    assert profile["highest_score"] == 94
    assert profile["average_confidence"] == 93
    assert profile["last_recruitment_title"] == "HRIS Product Owner"
    assert len(profile["application_history"]) == 2


def test_index_recruitment_talents_indexes_all_results(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "TALENT_POOL_DIR", tmp_path / "talent_pool")
    monkeypatch.setattr(store, "TALENT_INDEX_PATH", tmp_path / "talent_pool" / "talents.json")

    recruitment = {
        "id": "REC-003",
        "title": "Payroll Manager",
        "updated_at": "2026-07-04T10:00:00",
        "analysis_batch": {
            "results": [
                {
                    "candidate": {"name": "Emma Martin"},
                    "match_result": {
                        "overall_score": 88,
                        "confidence_score": 91,
                    },
                },
                {
                    "candidate": {"name": "John Smith"},
                    "match_result": {
                        "overall_score": 76,
                        "confidence_score": 82,
                    },
                },
            ]
        },
    }

    profiles = index_recruitment_talents(recruitment)

    assert len(profiles) == 2
    assert {profile["candidate_key"] for profile in profiles} == {
        "emma-martin",
        "john-smith",
    }
