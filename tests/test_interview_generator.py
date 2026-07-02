from talentcopilot.interview.interview_generator import generate_interview_guide


def test_generate_interview_guide_with_hris_profile():
    talent = {
        "name": "Emma Martin",
        "average_score": 91,
        "average_confidence": 94,
        "application_history": [
            {
                "score": 92,
                "recommendation": "Strong Hire",
                "updated_at": "2026-07-01T10:00:00",
                "executive_summary": "Strong HRIS implementation experience with Power BI reporting and API integration.",
            }
        ],
    }

    guide = generate_interview_guide(talent)

    assert guide["candidate_name"] == "Emma Martin"
    assert guide["best_recommendation"] == "Strong Hire"
    assert len(guide["technical_questions"]) > 0
    assert any("HRIS" in question for question in guide["technical_questions"])
    assert len(guide["behavioral_questions"]) > 0
    assert len(guide["role_fit_questions"]) > 0


def test_generate_interview_guide_adds_risk_questions_for_lower_scores():
    talent = {
        "name": "John Smith",
        "average_score": 68,
        "average_confidence": 72,
        "application_history": [
            {
                "score": 68,
                "recommendation": "Possible Backup",
                "updated_at": "2026-07-01T10:00:00",
                "executive_summary": "General HR background with limited system exposure.",
            }
        ],
    }

    guide = generate_interview_guide(talent)

    assert guide["candidate_name"] == "John Smith"
    assert len(guide["risk_validation_questions"]) >= 2


def test_generate_interview_guide_with_empty_history():
    talent = {
        "name": "Unknown Talent",
        "average_score": 0,
        "average_confidence": 0,
        "application_history": [],
    }

    guide = generate_interview_guide(talent)

    assert guide["candidate_name"] == "Unknown Talent"
    assert len(guide["technical_questions"]) >= 1
    assert len(guide["interview_focus"]) >= 1
