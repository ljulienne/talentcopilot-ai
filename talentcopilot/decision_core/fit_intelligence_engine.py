from talentcopilot.decision_core.evidence_intelligence_models import EvidenceIntelligenceReport
from talentcopilot.decision_core.fit_intelligence_models import (
    FitDriver,
    FitGap,
    FitIntelligenceReport,
    RoleRequirements,
)
from talentcopilot.decision_core.models import DecisionTraceStep, EvidenceGraph
from talentcopilot.services.skill_normalization import canonical_skill


class FitIntelligenceEngine:
    def evaluate(
        self,
        graph: EvidenceGraph,
        role: RoleRequirements,
        evidence_report: EvidenceIntelligenceReport | None = None,
    ) -> FitIntelligenceReport:
        skill_nodes = graph.find_nodes_by_type("skill")
        experience_nodes = graph.find_nodes_by_type("experience")
        achievement_nodes = graph.find_nodes_by_type("achievement")

        candidate_skills = {
            canonical_skill(node.label): node
            for node in skill_nodes
            if str(node.label or "").strip()
        }
        required = [
            canonical_skill(skill)
            for skill in role.required_skills
            if str(skill or "").strip()
        ]
        preferred = [
            canonical_skill(skill)
            for skill in role.preferred_skills
            if str(skill or "").strip()
        ]

        matched_required = [skill for skill in required if skill in candidate_skills]
        matched_preferred = [skill for skill in preferred if skill in candidate_skills]

        required_score = (
            int((len(matched_required) / len(required)) * 75)
            if required
            else (45 if skill_nodes else 0)
        )
        preferred_score = (
            int((len(matched_preferred) / max(1, len(preferred))) * 15)
            if preferred
            else 0
        )
        skill_match_score = min(
            100,
            required_score + preferred_score + (10 if skill_nodes else 0),
        )

        years = self._extract_years(experience_nodes)
        if role.minimum_years_experience <= 0:
            experience_score = 80 if years > 0 else 50
        else:
            experience_score = int(
                min(100, (years / role.minimum_years_experience) * 100)
            )

        achievement_score = min(100, len(achievement_nodes) * 35)

        evidence_adjustment = 0
        if evidence_report:
            if evidence_report.evidence_readiness_score < 40:
                evidence_adjustment = -10
            elif evidence_report.evidence_readiness_score >= 80:
                evidence_adjustment = 5

        fit_score = int(
            (skill_match_score * 0.55)
            + (experience_score * 0.25)
            + (achievement_score * 0.15)
            + evidence_adjustment
        )
        fit_score = max(0, min(100, fit_score))

        drivers = self._drivers(
            skill_nodes,
            experience_nodes,
            achievement_nodes,
            matched_required,
        )
        gaps = self._gaps(candidate_skills, role, years)

        status = self._status(fit_score)
        summary = (
            f"Fit score is {fit_score}%. "
            f"Skill match={skill_match_score}%, "
            f"experience match={experience_score}%, "
            f"achievement signal={achievement_score}%."
        )

        return FitIntelligenceReport(
            candidate_name=graph.candidate_name,
            role_title=role.role_title,
            fit_score=fit_score,
            skill_match_score=skill_match_score,
            experience_match_score=experience_score,
            achievement_signal_score=achievement_score,
            status=status,
            drivers=drivers,
            gaps=gaps,
            summary=summary,
        )

    def add_trace_step(self, trace, graph: EvidenceGraph, report: FitIntelligenceReport):
        trace.add_step(
            DecisionTraceStep(
                step_id=f"fit_intelligence_{graph.graph_id}",
                engine="FitIntelligenceEngine",
                action="EVALUATE_CANDIDATE_FIT",
                input_refs=[graph.graph_id],
                output_ref=str(report.fit_score),
                explanation=report.summary,
            )
        )
        return trace

    def _extract_years(self, experience_nodes) -> int:
        years = 0
        for node in experience_nodes:
            raw = node.metadata.get("years") if node.metadata else None
            try:
                years = max(years, int(float(raw)))
            except (TypeError, ValueError):
                continue
        return years

    def _drivers(self, skill_nodes, experience_nodes, achievement_nodes, matched_required):
        drivers = []
        canonical_nodes = {
            canonical_skill(node.label): node
            for node in skill_nodes
            if str(node.label or "").strip()
        }

        for skill in matched_required:
            node = canonical_nodes.get(skill)
            drivers.append(
                FitDriver(
                    area="Required skill",
                    detail=f"Candidate demonstrates required skill: {skill}.",
                    impact=12,
                    evidence_refs=[node.node_id] if node else [],
                )
            )

        if experience_nodes:
            drivers.append(
                FitDriver(
                    area="Experience",
                    detail="Candidate has explicit experience evidence.",
                    impact=10,
                    evidence_refs=[node.node_id for node in experience_nodes],
                )
            )

        if achievement_nodes:
            drivers.append(
                FitDriver(
                    area="Achievement",
                    detail=f"{len(achievement_nodes)} achievement evidence node(s) detected.",
                    impact=8,
                    evidence_refs=[node.node_id for node in achievement_nodes],
                )
            )

        return drivers

    def _gaps(self, candidate_skills, role, years):
        gaps = []

        for skill in role.required_skills:
            canonical = canonical_skill(skill)
            if canonical not in candidate_skills:
                gaps.append(
                    FitGap(
                        area="Required skill",
                        severity="High",
                        detail=f"Required skill not evidenced: {skill}.",
                    )
                )

        if years < role.minimum_years_experience:
            gaps.append(
                FitGap(
                    area="Experience",
                    severity="Medium",
                    detail=(
                        f"Candidate evidence shows {years} year(s), "
                        f"below required {role.minimum_years_experience}."
                    ),
                )
            )

        return gaps

    def _status(self, score: int) -> str:
        if score >= 85:
            return "Strong fit"
        if score >= 70:
            return "Good fit"
        if score >= 50:
            return "Partial fit"
        if score >= 30:
            return "Weak fit"
        return "No fit"
