from talentcopilot.talent_pool import talent_store as store


def test_update_talent_financial_data(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "TALENT_POOL_DIR", tmp_path / "talent_pool")
    monkeypatch.setattr(store, "TALENT_INDEX_PATH", tmp_path / "talent_pool" / "talents.json")

    store.upsert_talent_profile(
        {
            "candidate_key": "emma-martin",
            "name": "Emma Martin",
            "application_count": 1,
        }
    )

    updated = store.update_talent_financial_data(
        "emma-martin",
        {
            "budget_min": 70000,
            "budget_max": 85000,
            "expected_salary": 82000,
            "currency": "EUR",
        },
    )

    assert updated["financial_data"]["budget_min"] == 70000
    assert updated["financial_data"]["budget_max"] == 85000
    assert updated["financial_data"]["expected_salary"] == 82000
    assert updated["financial_data"]["currency"] == "EUR"

    loaded = store.find_talent_by_key("emma-martin")

    assert loaded["financial_data"]["expected_salary"] == 82000
