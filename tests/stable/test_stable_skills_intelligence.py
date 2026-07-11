from talentcopilot.organization_intelligence.models import EmployeeRecord
from talentcopilot.skills_intelligence import SkillsIntelligenceEngine, SkillsTaxonomy, skills_dataframe


def employees():
    return [
        EmployeeRecord("1", "Alice", "HR", skills=["SIRH", "gestion de projet", "paie"]),
        EmployeeRecord("2", "Bob", "IT", skills=["HRIS", "Python", "SQL"]),
        EmployeeRecord("3", "Claire", "Finance", skills=["Payroll", "Business Objects"]),
        EmployeeRecord("4", "David", "IT", skills=["Python", "Data Analytics"]),
    ]


def test_taxonomy_normalizes_multilingual_aliases():
    taxonomy = SkillsTaxonomy()
    assert taxonomy.canonicalize("SIRH") == "HRIS"
    assert taxonomy.canonicalize("gestion de projet") == "Project Management"
    assert taxonomy.canonicalize("paie") == "Payroll"


def test_engine_detects_strategic_gaps_and_rarity():
    report = SkillsIntelligenceEngine().analyze(
        employees(),
        strategic_skills=["HRIS", "SAP Payroll", "Python"],
    )
    assert report.employee_count == 4
    assert "SAP Payroll" in report.missing_strategic_skills
    hris = next(item for item in report.skills if item.canonical_name == "HRIS")
    assert hris.holder_count == 2
    assert hris.strategic is True
    assert report.insights


def test_engine_builds_department_coverage():
    report = SkillsIntelligenceEngine().analyze(employees(), strategic_skills=["HRIS", "Python"])
    departments = {item.department: item for item in report.departments}
    assert set(departments) == {"HR", "IT", "Finance"}
    assert "Python" in departments["HR"].missing_strategic_skills


def test_export_contains_skill_portfolio_columns():
    report = SkillsIntelligenceEngine().analyze(employees(), strategic_skills=["HRIS"])
    frame = skills_dataframe(report)
    assert {"skill", "rarity_score", "coverage_level", "holders"}.issubset(frame.columns)
