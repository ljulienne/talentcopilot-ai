from talentcopilot.services.import_safety_audit import ImportSafetyAudit


def test_import_safety_audit_critical_imports_pass():
    report = ImportSafetyAudit().audit()

    assert report["checked"]
    assert report["ok"], report["missing"]


def test_import_safety_audit_navigation_dict():
    report = ImportSafetyAudit().audit_navigation({
        "Home": ("talentcopilot.ui.home_v2", "render_home_v2"),
        "Reports": ("talentcopilot.ui.reports_v2", "render_reports_v2"),
    })

    assert report["ok"]
