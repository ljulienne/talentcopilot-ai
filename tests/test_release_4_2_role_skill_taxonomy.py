from talentcopilot.services.role_skill_taxonomy import (
    capability_set,
    capability_set_many,
    ordered_capabilities,
)


def test_verbose_job_requirements_map_to_official_capabilities():
    requirements = [
        "HRIS project management "
        "(implementations, migrations, process optimization, "
        "third-party interfaces)",
        "Knowledge of HR processes and HRIS tools, "
        "especially SAP SuccessFactors",
        "Proficiency in Power BI",
        "Change management, communication and training",
        "Experience in an international environment or large group",
        "Fluent French (oral and written)",
        "Fluent English (oral and written)",
    ]

    assert ordered_capabilities(requirements) == [
        "HRIS",
        "Project Management",
        "Change Management",
        "Reporting",
        "SAP SuccessFactors",
        "International Experience",
        "French",
        "English",
    ]


def test_candidate_labels_map_to_same_taxonomy():
    candidate = [
        "HRIS implementation and deployment",
        "Project Management",
        "Change Management",
        "Power BI reporting",
        "SuccessFactors",
        "International Experience",
        "French",
        "English",
    ]

    assert capability_set_many(candidate) == {
        "HRIS",
        "Project Management",
        "Change Management",
        "Reporting",
        "SAP SuccessFactors",
        "International Experience",
        "French",
        "English",
    }


def test_unrelated_skill_does_not_false_match():
    assert capability_set("Employee Relations") == set()
    assert capability_set("Diversity and Inclusion") == set()
