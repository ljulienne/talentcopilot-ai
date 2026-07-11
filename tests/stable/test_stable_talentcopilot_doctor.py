from pathlib import Path

from talentcopilot.doctor.cli import render_text
from talentcopilot.doctor.engine import TalentCopilotDoctor
from talentcopilot.doctor.models import CheckStatus, DoctorCheck, DoctorReport


REPO = Path(__file__).resolve().parents[2]


def test_doctor_models_and_text_renderer():
    report = DoctorReport(
        (
            DoctorCheck("One", CheckStatus.PASS, "Good"),
            DoctorCheck("Two", CheckStatus.WARN, "Review"),
        )
    )
    assert report.healthy is True
    assert len(report.warnings) == 1
    text = render_text(report)
    assert "Overall status: HEALTHY" in text
    assert "WARN" in text


def test_doctor_runs_against_repository_without_failures():
    report = TalentCopilotDoctor(REPO).run(include_git=False)
    assert report.failures == ()
    names = {check.name for check in report.checks}
    assert "Navigation" in names
    assert "Critical imports" in names
    assert "Test inventory" in names
