from talentcopilot.interview_intelligence_v2.evidence_gap_engine import EvidenceGapEngine
from talentcopilot.interview_intelligence_v2.models import InterviewQuestion, InterviewQuestionSet


class InterviewIntelligenceEngine:
    def generate(self, profile) -> InterviewQuestionSet:
        gaps = EvidenceGapEngine().detect(profile)
        questions = [self._question_from_gap(gap) for gap in gaps]

        summary = (
            f"{len(questions)} targeted interview question(s) generated for "
            f"{profile.candidate_name} based on Decision Core evidence gaps."
        )

        return InterviewQuestionSet(
            candidate_name=profile.candidate_name,
            role_title=profile.role_title,
            recommendation=profile.recommendation or "No recommendation",
            evidence_gaps=gaps,
            questions=questions,
            summary=summary,
        )

    def _question_from_gap(self, gap):
        if gap.area == "Role fit":
            return InterviewQuestion(
                area=gap.area,
                question="Can you describe a recent project that directly matches the key requirements of this role?",
                purpose="Validate whether the candidate has relevant transferable or direct experience.",
                expected_strong_answer="A concrete example with scope, responsibilities, stakeholders, outcomes and measurable impact.",
                positive_signals=[
                    "Specific project context",
                    "Clear ownership",
                    "Relevant skills demonstrated",
                    "Measurable outcomes",
                ],
                red_flags=[
                    "Generic answer",
                    "No direct role alignment",
                    "Cannot explain personal contribution",
                ],
                follow_ups=[
                    "What was your exact role?",
                    "What made this project difficult?",
                    "What result did you achieve?",
                ],
                evaluation_criteria=[
                    "Role relevance",
                    "Evidence specificity",
                    "Impact",
                    "Ownership",
                ],
            )

        if gap.area == "Decision confidence":
            return InterviewQuestion(
                area=gap.area,
                question="What evidence can you provide that best demonstrates your fit for this role?",
                purpose="Collect missing evidence to improve decision confidence.",
                expected_strong_answer="The candidate provides concrete examples, metrics, deliverables or references aligned with the role.",
                positive_signals=[
                    "Provides concrete evidence",
                    "Mentions measurable results",
                    "Links experience to role requirements",
                ],
                red_flags=[
                    "Cannot provide examples",
                    "Relies only on claims",
                    "Evidence does not match role needs",
                ],
                follow_ups=[
                    "Can you quantify the outcome?",
                    "Who can validate this work?",
                    "What artifact or deliverable did you produce?",
                ],
                evaluation_criteria=[
                    "Evidence quality",
                    "Traceability",
                    "Relevance",
                ],
            )

        if gap.area == "Hiring risk":
            return InterviewQuestion(
                area=gap.area,
                question="What risks or challenges do you anticipate in this role, and how would you mitigate them?",
                purpose="Validate candidate awareness, maturity and ability to manage role-specific risk.",
                expected_strong_answer="A realistic risk assessment with mitigation steps and examples from past experience.",
                positive_signals=[
                    "Acknowledges real risks",
                    "Proposes practical mitigations",
                    "Shows self-awareness",
                ],
                red_flags=[
                    "Dismisses all risk",
                    "Blames others",
                    "No mitigation strategy",
                ],
                follow_ups=[
                    "Which risk would you address first?",
                    "What support would you need?",
                    "How have you handled a similar issue before?",
                ],
                evaluation_criteria=[
                    "Risk awareness",
                    "Mitigation quality",
                    "Judgment",
                ],
            )

        if gap.area == "Compensation feasibility":
            return InterviewQuestion(
                area=gap.area,
                question="How flexible are your compensation expectations, and which elements matter most to you?",
                purpose="Assess financial feasibility without confusing budget fit with candidate quality.",
                expected_strong_answer="Clear expectations, flexibility range and openness to total rewards discussion.",
                positive_signals=[
                    "Transparent expectations",
                    "Understands total package",
                    "Shows flexibility",
                ],
                red_flags=[
                    "No flexibility",
                    "Expectations far above range",
                    "Unclear priorities",
                ],
                follow_ups=[
                    "What is your minimum acceptable package?",
                    "Would benefits or flexibility influence your decision?",
                    "What timing constraints do you have?",
                ],
                evaluation_criteria=[
                    "Feasibility",
                    "Flexibility",
                    "Clarity",
                ],
            )

        return InterviewQuestion(
            area=gap.area,
            question="What motivates you about this role, and what evidence best supports your readiness?",
            purpose="Confirm motivation and validate strongest evidence.",
            expected_strong_answer="A role-specific answer connected to concrete past achievements.",
            positive_signals=["Role motivation", "Evidence-based answer", "Clear examples"],
            red_flags=["Generic motivation", "No evidence", "Misunderstands role"],
            follow_ups=["Why this role now?", "What would make you successful?", "What evidence should we rely on?"],
            evaluation_criteria=["Motivation", "Evidence quality", "Role understanding"],
        )
