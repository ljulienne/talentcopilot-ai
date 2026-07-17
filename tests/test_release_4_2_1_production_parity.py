from pathlib import Path


def test_isolated_worker_uses_repository_source_first():
    source = Path(
        "talentcopilot/services/"
        "isolated_recruitment_upload_worker.py"
    ).read_text(encoding="utf-8")

    assert "_REPO_ROOT" in source
    assert "sys.path.insert(0, str(_REPO_ROOT))" in source


def test_isolated_service_executes_the_canonical_worker():
    service_source = Path(
        "talentcopilot/services/"
        "isolated_recruitment_upload_service.py"
    ).read_text(encoding="utf-8")

    worker_source = Path(
        "talentcopilot/services/"
        "isolated_recruitment_upload_worker.py"
    ).read_text(encoding="utf-8")

    # The service must execute the dedicated isolated worker.
    assert "isolated_recruitment_upload_worker" in service_source
    assert "subprocess" in service_source

    # The worker must prioritize the current repository source.
    assert "_REPO_ROOT" in worker_source
    assert "sys.path.insert(0, str(_REPO_ROOT))" in worker_source

def test_official_ranking_uses_match_score_only():
    source = Path(
        "talentcopilot/services/"
        "recruitment_upload_session_service.py"
    ).read_text(encoding="utf-8")

    marker = (
        "the official recruitment rank derives exclusively "
        "from the"
    )

    assert marker in source
    assert "-float(item.match_score or 0)" in source

    ranking_block = source[source.index(marker):]

    assert "item.rank or 9999" not in ranking_block
