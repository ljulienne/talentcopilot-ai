from __future__ import annotations

import re

from talentcopilot.organization_intelligence.models import KnowledgeDiagnostic, SkillRisk

from .engine import InsightEngine
from .models import OrganizationInsight


class KnowledgeInsightAdapter:
    def __init__(self, engine: InsightEngine | None = None):
        self.engine = engine or InsightEngine()

    def from_diagnostic(self, diagnostic: KnowledgeDiagnostic, limit: int = 10) -> list[OrganizationInsight]:
        return [self.from_skill_risk(risk) for risk in diagnostic.skill_risks[:limit]]

    def from_skill_risk(self, risk: SkillRisk) -> OrganizationInsight:
        severity = "Critical" if risk.risk_score >= 90 else risk.risk_level
        confidence = self._confidence(risk)
        evidence = [
            {"label": "Holder coverage", "detail": f"{len(risk.holders)} holder(s): {', '.join(risk.holders) or 'none'}", "strength": 0.95},
            {"label": "Backup coverage", "detail": f"{len(risk.backups)} backup(s): {', '.join(risk.backups) or 'none'}", "strength": 0.9},
        ]
        evidence.extend(
            {"label": "Risk driver", "detail": reason, "strength": 0.8}
            for reason in risk.reasons[:3]
        )
        recommendations = [
            {
                "action": action,
                "priority": "Immediate" if severity in {"Critical", "High"} else "Planned",
                "timeframe": "0-90 days" if severity in {"Critical", "High"} else "Next workforce cycle",
                "business_value": "Reduce continuity risk and distribute critical knowledge.",
            }
            for action in risk.recommendations
        ]
        slug = re.sub(r"[^a-z0-9]+", "-", risk.skill.casefold()).strip("-") or "skill"
        return self.engine.build(
            insight_id=f"knowledge-{slug}",
            title=f"Knowledge concentration on {risk.skill}",
            category="Knowledge",
            severity=severity,
            confidence=confidence,
            current_situation=(
                f"{risk.skill} is held by {len(risk.holders)} person(s) across "
                f"{len(risk.departments)} department(s), with {len(risk.backups)} identified backup(s)."
            ),
            business_impact="Business continuity may be disrupted if the current knowledge holders become unavailable.",
            evidence=evidence,
            recommendations=recommendations,
        )

    @staticmethod
    def _confidence(risk: SkillRisk) -> float:
        score = 0.58
        if risk.holders:
            score += 0.12
        if risk.reasons:
            score += 0.12
        if risk.critical:
            score += 0.08
        if risk.departments:
            score += 0.05
        return min(0.95, score)
