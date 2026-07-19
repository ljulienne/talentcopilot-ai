from talentcopilot.services.report_export_service import ReportExportService


def test_unified_report_export_returns_valid_pdf():
    export = ReportExportService().from_markdown(
        "# Recruitment Mission\n\n## Official ranking\n\n1. **Alex Doe** - 82% - Recommended",
        file_name="talentcopilot_recruitment_mission.md",
        title="TalentCopilot Recruitment Mission Brief",
    )
    assert export.data.startswith(b"%PDF")
    assert len(export.data) > 500
    assert export.file_name == "talentcopilot_recruitment_mission.pdf"
    assert export.mime == "application/pdf"


def test_unified_report_export_preserves_pdf_extension():
    export = ReportExportService().from_markdown(
        "Executive summary",
        file_name="executive_report.pdf",
        title="Executive Report",
    )
    assert export.file_name == "executive_report.pdf"
    assert export.data.startswith(b"%PDF")


def test_unified_report_export_does_not_expose_markdown_mime():
    export = ReportExportService().from_markdown(
        "Report",
        file_name="report",
        title="Report",
    )
    assert export.mime != "text/markdown"
    assert export.file_name.endswith(".pdf")
