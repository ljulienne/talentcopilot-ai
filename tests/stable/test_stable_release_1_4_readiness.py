from pathlib import Path

from talentcopilot.doctor.checks import check_executive_copilot_readiness
from talentcopilot.doctor.models import CheckStatus
from talentcopilot.release_health import load_release_manifest, validate_release_files


def test_release_1_4_manifest_is_complete():
    repo = Path(__file__).resolve().parents[2]
    manifest = load_release_manifest(repo, "1.4")
    assert manifest.release == "1.4"
    assert not validate_release_files(repo, manifest)


def test_doctor_reports_executive_copilot_ready():
    repo = Path(__file__).resolve().parents[2]
    check = check_executive_copilot_readiness(repo)
    assert check.status is CheckStatus.PASS
