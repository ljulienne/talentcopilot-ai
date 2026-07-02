from pathlib import Path

import pytest

from talentcopilot.storage import recruitment_store as store


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    recruitments_dir = data_dir / "recruitments"

    monkeypatch.setattr(store, "DATA_DIR", data_dir)
    monkeypatch.setattr(store, "RECRUITMENTS_DIR", recruitments_dir)

    return recruitments_dir


def test_save_and_load_recruitment(isolated_storage):
    data = {
        "id": "REC-TEST-001",
        "title": "HRIS Project Manager",
        "language": "English",
        "analysis_batch": {"results": []},
    }

    saved = store.save_recruitment(data)
    loaded = store.load_recruitment("REC-TEST-001")

    assert saved["id"] == "REC-TEST-001"
    assert loaded["title"] == "HRIS Project Manager"
    assert "created_at" in loaded
    assert "updated_at" in loaded


def test_list_recruitments_counts_candidates(isolated_storage):
    store.save_recruitment(
        {
            "id": "REC-TEST-002",
            "title": "Recruitment With Candidates",
            "analysis_batch": {
                "results": [
                    {"candidate": {"name": "Alice"}},
                    {"candidate": {"name": "Bob"}},
                ]
            },
        }
    )

    recruitments = store.list_recruitments()

    assert len(recruitments) == 1
    assert recruitments[0]["candidate_count"] == 2


def test_delete_recruitment(isolated_storage):
    store.save_recruitment(
        {
            "id": "REC-TEST-003",
            "title": "To Delete",
        }
    )

    assert store.delete_recruitment("REC-TEST-003") is True
    assert store.delete_recruitment("REC-TEST-003") is False

    with pytest.raises(FileNotFoundError):
        store.load_recruitment("REC-TEST-003")


def test_update_recruitment_preserves_id_and_created_at(isolated_storage):
    saved = store.save_recruitment(
        {
            "id": "REC-TEST-004",
            "title": "Original Title",
        }
    )

    updated = store.update_recruitment(
        "REC-TEST-004",
        {
            "id": "SHOULD-NOT-CHANGE",
            "created_at": "SHOULD-NOT-CHANGE",
            "title": "Updated Title",
        },
    )

    assert updated["id"] == "REC-TEST-004"
    assert updated["created_at"] == saved["created_at"]
    assert updated["title"] == "Updated Title"


def test_duplicate_recruitment_creates_copy(isolated_storage, monkeypatch):
    store.save_recruitment(
        {
            "id": "REC-TEST-005",
            "title": "Original Recruitment",
        }
    )

    monkeypatch.setattr(store, "generate_recruitment_id", lambda: "REC-TEST-005-COPY")

    duplicated = store.duplicate_recruitment("REC-TEST-005")

    assert duplicated["id"] == "REC-TEST-005-COPY"
    assert duplicated["title"] == "Original Recruitment - Copy"
    assert store.load_recruitment("REC-TEST-005")["title"] == "Original Recruitment"
