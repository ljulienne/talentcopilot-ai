from talentcopilot.models.product_readiness import (
    ProductReadinessReport,
    ReadinessCheck,
    ReadinessLevel,
    ReadinessSeverity,
)


def test_product_readiness_report_counts():
    report = ProductReadinessReport(
        product_name="TalentCopilot-AI",
        version="v0.7.2",
        readiness_score=80,
        readiness_level=ReadinessLevel.GOOD,
        checks=[
            ReadinessCheck("A", True, ReadinessSeverity.INFO, "OK"),
            ReadinessCheck("B", False, ReadinessSeverity.CRITICAL, "Broken"),
        ],
    )

    assert report.passed_count == 1
    assert report.failed_count == 1
    assert report.critical_count == 1
