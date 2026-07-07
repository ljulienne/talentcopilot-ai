from talentcopilot.ai.talent_locator_engine import TalentLocatorEngine
from talentcopilot.models.talent_locator import TalentLocatorFit


def test_talent_locator_ranks_best_candidate_first():
    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
        "keywords": ["transformation"],
    }

    talent_pool = [
        {
            "name": "Bob",
            "skills": ["Excel"],
            "years_experience": 2,
            "achievements": ["Prepared reports"],
        },
        {
            "name": "Alice",
            "skills": ["Project Management", "Stakeholder Management"],
            "years_experience": 8,
            "achievements": [
                "Led transformation project",
                "Managed stakeholder governance",
                "Improved adoption by 35%",
            ],
        },
    ]

    report = TalentLocatorEngine().locate(job, talent_pool)

    assert report.total_candidates == 2
    assert report.results[0].candidate_name == "Alice"
    assert report.results[0].locator_score >= report.results[1].locator_score
    assert report.results[0].fit in {
        TalentLocatorFit.EXCELLENT,
        TalentLocatorFit.STRONG,
        TalentLocatorFit.MODERATE,
    }


def test_talent_locator_handles_empty_pool():
    report = TalentLocatorEngine().locate(
        {"title": "Data Engineer", "required_skills": ["Python"]},
        [],
    )

    assert report.total_candidates == 0
    assert report.results == []
