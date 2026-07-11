from __future__ import annotations

import pandas as pd

from .models import WorkforceScenarioReport


def successors_dataframe(report: WorkforceScenarioReport) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "employee_id": item.employee_id,
            "name": item.name,
            "department": item.department,
            "role": item.role,
            "readiness_score": item.readiness_score,
            "matched_skills": "; ".join(item.matched_skills),
            "missing_skills": "; ".join(item.missing_skills),
            "rationale": "; ".join(item.rationale),
        }
        for item in report.impact.successor_candidates
    ])
