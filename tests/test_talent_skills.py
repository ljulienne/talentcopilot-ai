from talentcopilot.talent_pool.talent_skills import (
    calculate_skill_coverage,
    detect_skills,
    enrich_talent_with_skills,
)


def test_detect_skills_from_application_history():
    talent = {
        "application_history": [
            {
                "recruitment_title": "HRIS Project Manager",
                "recommendation": "Strong Hire",
                "executive_summary": "Strong Workday implementation experience with Power BI reporting and API integration.",
            }
        ]
    }

    skills = detect_skills(talent)

    assert "HRIS" in skills
    assert "Project Management" in skills
    assert "Data" in skills
    assert "Integration" in skills


def test_calculate_skill_coverage():
    talent = {
        "application_history": [
            {
                "executive_summary": "HRIS, payroll, Power BI, API integration and change management experience.",
            }
        ]
    }

    coverage = calculate_skill_coverage(talent)

    assert coverage > 0


def test_enrich_talent_with_skills():
    talent = {
        "name": "Emma Martin",
        "application_history": [
            {
                "executive_summary": "Experienced in SAP SuccessFactors, payroll and recruitment analytics.",
            }
        ],
    }

    enriched = enrich_talent_with_skills(talent)

    assert enriched["name"] == "Emma Martin"
    assert "detected_skills" in enriched
    assert "skill_coverage" in enriched
    assert enriched["skill_coverage"] > 0
