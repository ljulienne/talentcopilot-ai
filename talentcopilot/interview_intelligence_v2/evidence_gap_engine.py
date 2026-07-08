from talentcopilot.interview_intelligence_v2.models import EvidenceGapItem


class EvidenceGapEngine:
    def detect(self, profile) -> list[EvidenceGapItem]:
        gaps = []
        metadata = profile.metadata or {}

        fit_score = int(float(metadata.get("fit_score", profile.fit_score or 0)))
        confidence_score = int(float(metadata.get("confidence_score", profile.confidence_score or 0)))
        risk_level = metadata.get("risk_level", profile.risk_level or "Medium")
        budget_fit = metadata.get("budget_fit_score")

        if fit_score < 50:
            gaps.append(
                EvidenceGapItem(
                    area="Role fit",
                    severity="High",
                    detail="Candidate fit is below interview threshold.",
                    reason="Validate whether the candidate has transferable or missing evidence before advancing.",
                )
            )

        if confidence_score < 65:
            gaps.append(
                EvidenceGapItem(
                    area="Decision confidence",
                    severity="Medium",
                    detail="Analysis confidence is limited.",
                    reason="More evidence is required before a reliable decision can be made.",
                )
            )

        if risk_level in {"High", "Critical"}:
            gaps.append(
                EvidenceGapItem(
                    area="Hiring risk",
                    severity="High",
                    detail=f"Risk level is {risk_level}.",
                    reason="Risk factors must be validated or mitigated in interview.",
                )
            )

        if budget_fit is not None:
            try:
                budget_score = int(float(budget_fit))
                if budget_score < 60:
                    gaps.append(
                        EvidenceGapItem(
                            area="Compensation feasibility",
                            severity="Medium",
                            detail=f"Budget fit is {budget_score}%.",
                            reason="Compensation expectations may require negotiation or approval.",
                        )
                    )
            except ValueError:
                pass

        if not gaps:
            gaps.append(
                EvidenceGapItem(
                    area="Final validation",
                    severity="Low",
                    detail="No major blocking gap detected.",
                    reason="Interview should validate the strongest evidence and confirm motivation.",
                )
            )

        return gaps
