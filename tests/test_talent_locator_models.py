from talentcopilot.models.talent_locator import (
    TalentLocatorCandidate,
    TalentLocatorFit,
    TalentLocatorReport,
)


def test_talent_locator_report_counts_recommended_profiles():
    report = TalentLocatorReport(
        role_title="Transformation Lead",
        total_candidates=2,
        results=[
            TalentLocatorCandidate(
                candidate_name="Alice",
                role_title="Transformation Lead",
                locator_score=88,
                fit=TalentLocatorFit.EXCELLENT,
            ),
            TalentLocatorCandidate(
                candidate_name="Bob",
                role_title="Transformation Lead",
                locator_score=42,
                fit=TalentLocatorFit.WEAK,
            ),
        ],
    )

    assert report.recommended_count == 1
    assert report.results[0].is_recommended is True
