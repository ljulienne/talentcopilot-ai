from __future__ import annotations

import pandas as pd

from .models import SkillsIntelligenceReport


def skills_dataframe(report: SkillsIntelligenceReport) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "skill": item.canonical_name,
                "category": item.category,
                "strategic": item.strategic,
                "gap_status": item.gap_status,
                "holder_count": item.holder_count,
                "department_count": item.department_count,
                "rarity_score": item.rarity_score,
                "coverage_level": item.coverage_level,
                "holders": "; ".join(item.holders),
                "departments": "; ".join(item.departments),
                "recommendations": "; ".join(item.recommendations),
            }
            for item in report.skills
        ]
    )
