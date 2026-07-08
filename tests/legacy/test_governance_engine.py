from talentcopilot.ai.governance_engine import GovernanceEngine


def test_governance_engine_outputs_decision_card():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
        "years_experience": 8,
        "achievements": [
            "Led Project Management transformation and improved adoption by 35%",
            "Managed Stakeholder Management governance across 6 departments",
        ],
    }

    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
    }

    report = GovernanceEngine().assess_candidate(candidate, job, match_score=88)

    assert report.decision_card.candidate_name == "Alice Martin"
    assert report.decision_card.role_title == "Transformation Lead"
    assert report.decision_card.confidence_score >= 0
    assert report.decision_card.evidence_quality_score >= 0
    assert report.decision_card.decision in {
        "Strong Hire",
        "Hire / Continue Process",
        "Review Carefully",
        "Not Recommended",
    }


def test_governance_engine_is_safe_with_empty_inputs():
    candidate = {"name": "Unknown"}
    job = {"title": "Unknown Role", "required_skills": ["Python"]}

    report = GovernanceEngine().assess_candidate(candidate, job, match_score=0)

    assert report.decision_card.risk_level in {"Low", "Medium", "High"}
    assert report.decision_card.human_validation in {
        "Standard Review",
        "Recommended",
        "Strongly Recommended",
    }
