from __future__ import annotations

import hashlib

from talentcopilot.intelligence_core.models import OrganizationInsight

from .models import RegisteredEvidence


class EvidenceRegistry:
    """Normalizes evidence emitted by heterogeneous domain engines."""

    def register(self, insights: list[OrganizationInsight]) -> tuple[RegisteredEvidence, ...]:
        items: list[RegisteredEvidence] = []
        seen: set[str] = set()
        for insight in insights:
            source = insight.category or "Organization"
            for evidence in insight.evidence:
                raw = f"{insight.insight_id}|{evidence.label}|{evidence.detail}|{source}"
                evidence_id = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
                if evidence_id in seen:
                    continue
                seen.add(evidence_id)
                items.append(
                    RegisteredEvidence(
                        evidence_id=evidence_id,
                        source_engine=source,
                        label=evidence.label,
                        detail=evidence.detail,
                        confidence=min(1.0, max(0.0, evidence.strength * insight.confidence)),
                        severity=insight.severity.value,
                    )
                )
        return tuple(items)
