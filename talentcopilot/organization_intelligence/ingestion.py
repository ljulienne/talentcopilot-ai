from __future__ import annotations

import io
import re
from typing import Iterable

import pandas as pd

from .models import EmployeeRecord


COLUMN_ALIASES = {
    "employee_id": ["employee_id", "employee id", "id", "matricule", "employeeid"],
    "name": ["name", "employee", "employee_name", "employee name", "nom", "full_name"],
    "department": ["department", "dept", "service", "business_unit", "business unit"],
    "role": ["role", "job", "job_title", "job title", "position", "poste"],
    "manager": ["manager", "manager_name", "manager name", "supervisor", "responsable"],
    "skills": ["skills", "skill", "competencies", "competences", "compétences"],
    "critical_skills": ["critical_skills", "critical skills", "skills_critical", "compétences critiques"],
    "backup_for": ["backup_for", "backup for", "backup", "successor_for"],
    "retirement_risk": ["retirement_risk", "retirement risk", "retirement_soon", "retraite_proche"],
    "documentation_level": ["documentation_level", "documentation level", "documentation"],
}


def _norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower()).strip()


def _split(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [x.strip() for x in re.split(r"[;,|\n]", str(value)) if x.strip()]


def _as_bool(value: object) -> bool:
    return _norm(value) in {"1", "true", "yes", "y", "oui", "high", "elevated"}


def map_columns(columns: Iterable[str]) -> dict[str, str]:
    normalized = {_norm(c): c for c in columns}
    result: dict[str, str] = {}
    for target, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            found = normalized.get(_norm(alias))
            if found is not None:
                result[target] = found
                break
    return result


def dataframe_to_employees(df: pd.DataFrame) -> list[EmployeeRecord]:
    mapping = map_columns(df.columns)
    required = ["name", "department", "skills"]
    missing = [c for c in required if c not in mapping]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    records: list[EmployeeRecord] = []
    for idx, row in df.fillna("").iterrows():
        name = str(row[mapping["name"]]).strip()
        if not name:
            continue
        records.append(
            EmployeeRecord(
                employee_id=str(row[mapping.get("employee_id", mapping["name"])]).strip() or str(idx + 1),
                name=name,
                department=str(row[mapping["department"]]).strip() or "Unknown",
                role=str(row[mapping["role"]]).strip() if "role" in mapping else "",
                manager=str(row[mapping["manager"]]).strip() if "manager" in mapping else "",
                skills=_split(row[mapping["skills"]]),
                critical_skills=_split(row[mapping["critical_skills"]]) if "critical_skills" in mapping else [],
                backup_for=_split(row[mapping["backup_for"]]) if "backup_for" in mapping else [],
                retirement_risk=_as_bool(row[mapping["retirement_risk"]]) if "retirement_risk" in mapping else False,
                documentation_level=str(row[mapping["documentation_level"]]).strip().lower() if "documentation_level" in mapping else "unknown",
            )
        )
    if not records:
        raise ValueError("No valid employee rows found.")
    return records


def load_uploaded_file(uploaded_file) -> list[EmployeeRecord]:
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()
    if name.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(data))
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(data), encoding="latin-1")
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(data))
    else:
        raise ValueError("Unsupported format. Upload a CSV or Excel file.")
    return dataframe_to_employees(df)
