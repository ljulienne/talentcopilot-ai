from talentcopilot.hybrid_matching.interview_models import HybridInterviewPlan, HybridInterviewQuestion

class HybridInterviewFocusEngine:
    def build(self, hybrid_report) -> HybridInterviewPlan:
        questions = []
        recruiter_report = hybrid_report.recruiter_report
        gaps = list(recruiter_report.gaps if recruiter_report else hybrid_report.semantic_skill_report.missing_skills)

        for gap in gaps[:4]:
            questions.append(self._gap_question(gap))

        if hybrid_report.career_report:
            if hybrid_report.career_report.leadership_score < 60:
                questions.append(self._leadership_question())
            if hybrid_report.career_report.impact_score < 60:
                questions.append(self._impact_question())
            if hybrid_report.career_report.transformation_score < 60:
                questions.append(self._transformation_question())

        if not questions:
            questions.append(self._depth_question())

        return HybridInterviewPlan(hybrid_report.candidate_name, hybrid_report.role_title, questions[:6])

    def _gap_question(self, gap: str) -> HybridInterviewQuestion:
        return HybridInterviewQuestion(
            focus_area=gap,
            question=f"Can you describe a concrete project where you used or delivered {gap}?",
            follow_up=f"What was your exact role, what complexity did you face, and what measurable outcome did you achieve with {gap}?",
            strong_signal="Specific example with context, responsibility, actions and measurable results.",
            red_flag="Generic exposure without hands-on responsibility.",
            evaluation_criterion=f"Depth and credibility of practical experience with {gap}.",
        )

    def _leadership_question(self) -> HybridInterviewQuestion:
        return HybridInterviewQuestion(
            "Leadership",
            "Can you describe the largest team or stakeholder group you had to lead or influence?",
            "How did you handle resistance, prioritization and decision-making?",
            "Clear leadership scope, ownership, conflict management and delivery.",
            "No clear responsibility or accountability.",
            "Leadership scope and ability to drive outcomes through people.",
        )

    def _impact_question(self) -> HybridInterviewQuestion:
        return HybridInterviewQuestion(
            "Business Impact",
            "What is the most measurable business impact you delivered in an HR or HRIS project?",
            "How was the impact measured and what was your personal contribution?",
            "Quantified results such as adoption, cost reduction, efficiency or quality.",
            "No quantified outcome or unclear personal contribution.",
            "Ability to connect work to business outcomes.",
        )

    def _transformation_question(self) -> HybridInterviewQuestion:
        return HybridInterviewQuestion(
            "Transformation",
            "Tell me about a transformation or change management initiative you led.",
            "How did you secure adoption and manage stakeholders?",
            "Structured change approach, stakeholder strategy and adoption evidence.",
            "Focus only on system go-live without adoption.",
            "Transformation delivery and change adoption maturity.",
        )

    def _depth_question(self) -> HybridInterviewQuestion:
        return HybridInterviewQuestion(
            "Critical Role Requirements",
            "Which experience best proves your readiness for this role?",
            "What were the stakes, your exact responsibility and the measurable result?",
            "Relevant, detailed, role-aligned evidence.",
            "Generic answer with little link to the role.",
            "Overall relevance and evidence quality.",
        )
