from talentcopilot.ai.evidence_quality_engine import EvidenceQualityEngine


def test_evidence_quality_engine_scores_measurable_evidence():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
        "achievements": [
            "Led a Project Management transformation and improved adoption by 35%",
            "Managed Stakeholder Management workshops with business leaders",
        ],
    }

    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
    }

    summary = EvidenceQualityEngine().assess(candidate, job)

    assert summary.overall_quality_score > 0
    assert len(summary.assessments) == 2
    assert summary.assessments[0].evidence_count >= 1
