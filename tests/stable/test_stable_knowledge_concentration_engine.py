import pandas as pd

from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees, map_columns
from talentcopilot.organization_intelligence.knowledge_engine import KnowledgeConcentrationEngine


def test_column_mapping_accepts_hr_aliases():
    mapping = map_columns(["Matricule", "Nom", "Service", "Compétences"])
    assert mapping["employee_id"] == "Matricule"
    assert mapping["name"] == "Nom"
    assert mapping["department"] == "Service"
    assert mapping["skills"] == "Compétences"


def test_engine_detects_single_holder_critical_skill():
    df = pd.DataFrame([
        {"name": "Alice", "department": "HR", "skills": "SAP Payroll; Excel", "critical_skills": "SAP Payroll", "backup_for": "", "documentation_level": "low"},
        {"name": "Bob", "department": "IT", "skills": "Python; SQL", "critical_skills": "", "backup_for": "", "documentation_level": "high"},
    ])
    diagnostic = KnowledgeConcentrationEngine().analyze(dataframe_to_employees(df))
    sap = next(r for r in diagnostic.skill_risks if r.skill == "SAP Payroll")
    assert sap.risk_level == "High"
    assert sap.risk_score >= 70
    assert "Alice" in sap.holders
    assert diagnostic.high_risk_count >= 1


def test_engine_rewards_distributed_coverage():
    df = pd.DataFrame([
        {"name": f"Employee {i}", "department": "IT" if i % 2 else "HR", "skills": "Python", "backup_for": "Python" if i == 1 else "", "documentation_level": "high"}
        for i in range(1, 7)
    ])
    diagnostic = KnowledgeConcentrationEngine().analyze(dataframe_to_employees(df))
    python_risk = diagnostic.skill_risks[0]
    assert python_risk.risk_level == "Low"
    assert python_risk.risk_score < 40
