from talentcopilot.services.versioning import get_app_name, get_app_version, get_version_summary


def test_versioning_service():
    assert get_app_name()
    assert get_app_version().startswith("v")
    assert get_app_name() in get_version_summary()
