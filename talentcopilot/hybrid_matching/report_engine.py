from talentcopilot.hybrid_matching.report_models import HybridRecruiterReport


class HybridRecruiterReportEngine:
    def build(self, hybrid_report) -> HybridRecruiterReport:
        explanation = hybrid_report.explanation_report
        score = hybrid_report.hybrid_score

        readiness = self._readiness(score)
        strengths = self._strengths(hybrid_report)
        gaps = self._gaps(hybrid_report)
        interview_focus = self._interview_focus(hybrid_report, gaps)
        action = self._action(score, gaps)

        summary = (
            f"{hybrid_report.candidate_name} is assessed as {readiness} for {hybrid_report.role_title}. "
            f"The profile shows a hybrid score of {score}%, with semantic score {hybrid_report.semantic_score}% "
            f"and career score {hybrid_report.career_score}%. "
            f"{explanation.recruiter_summary if explanation else hybrid_report.summary}"
        )

        return HybridRecruiterReport(
            candidate_name=hybrid_report.candidate_name,
            role_title=hybrid_report.role_title,
            readiness_level=readiness,
            executive_summary=summary,
            top_strengths=strengths,
            gaps=gaps,
            interview_focus=interview_focus,
            action_recommendation=action,
        )

    def _readiness(self, score: int) -> str:
        if score >= 80:
            return "Strong fit"
        if score >= 65:
            return "Qualified with validation points"
        if score >= 50:
            return "Partial fit"
        return "Low fit"

    def _strengths(self, report) -> list[str]:
        strengths = []

        for match in report.semantic_skill_report.matches:
            if match.score >= 80:
                strengths.append(f"{match.required_skill}: {match.explanation}")

        if report.career_report:
            for signal in report.career_report.signals:
                if signal.score >= 70:
                    strengths.append(f"{signal.category}: {signal.label}")

        return strengths[:6]

    def _gaps(self, report) -> list[str]:
        gaps = list(report.semantic_skill_report.missing_skills)

        if report.explanation_report:
            for penalty in report.explanation_report.penalties:
                for evidence in penalty.evidence:
                    if evidence not in gaps:
                        gaps.append(evidence)

        return gaps[:6]

    def _interview_focus(self, report, gaps: list[str]) -> list[str]:
        focus = []

        for gap in gaps:
            focus.append(f"Validate practical experience with {gap}.")

        if report.career_report and report.career_report.leadership_score < 60:
            focus.append("Clarify leadership scope and team management responsibilities.")

        if report.career_report and report.career_report.impact_score < 60:
            focus.append("Ask for quantified business outcomes and measurable achievements.")

        if not focus:
            focus.append("Validate depth of experience on the most critical role requirements.")

        return focus[:6]

    def _action(self, score: int, gaps: list[str]) -> str:
        if score >= 80 and len(gaps) <= 1:
            return "Prioritize for interview"
        if score >= 65:
            return "Interview with targeted validation"
        if score >= 50:
            return "Review before shortlisting"
        return "Do not prioritize"
