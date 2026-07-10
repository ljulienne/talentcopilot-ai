import pandas as pd


def demo_dataframe() -> pd.DataFrame:
    return pd.DataFrame([
        {"employee_id":"E001","name":"Marie Dupont","department":"HR","role":"HRIS Lead","skills":"SAP Payroll; HRIS Architecture; Business Objects","critical_skills":"SAP Payroll; HRIS Architecture","backup_for":"","retirement_risk":"no","documentation_level":"low"},
        {"employee_id":"E002","name":"Thomas Lee","department":"IT","role":"Integration Engineer","skills":"API Integration; Python; Data Engineering","critical_skills":"API Integration","backup_for":"HRIS Architecture","retirement_risk":"no","documentation_level":"medium"},
        {"employee_id":"E003","name":"Sofia Martin","department":"Finance","role":"Payroll Analyst","skills":"Payroll Control; Excel; SAP Payroll","critical_skills":"","backup_for":"SAP Payroll","retirement_risk":"no","documentation_level":"high"},
        {"employee_id":"E004","name":"David Smith","department":"Operations","role":"Reporting Specialist","skills":"Business Objects; Reporting; SQL","critical_skills":"Business Objects","backup_for":"","retirement_risk":"yes","documentation_level":"low"},
        {"employee_id":"E005","name":"Alice Chen","department":"IT","role":"Data Analyst","skills":"SQL; Python; Reporting","critical_skills":"","backup_for":"Business Objects","retirement_risk":"no","documentation_level":"medium"},
        {"employee_id":"E006","name":"Jean Morel","department":"HR","role":"HR Project Manager","skills":"Change Management; Project Management; HRIS Architecture","critical_skills":"","backup_for":"","retirement_risk":"no","documentation_level":"medium"},
    ])
