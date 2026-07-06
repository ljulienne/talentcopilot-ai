from dataclasses import dataclass, field
from typing import List

from talentcopilot.ai.reasoning_engine import CandidateReasoningReport


@dataclass
class InterviewQuestion:
    question: str
    objective: str
    evidence_to_validate: List[str] = field(default_factory=list)
    strong_answer_should_include: List[str] = field(default_factory=list)
    positive_signals: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    evaluation_criteria: List[str] = field(default_factory=list)


@dataclass
class InterviewGuide:
    candidate_name: str
    role_title: str
    interview_focus: str
    questions: List[InterviewQuestion]
    closing_recommendation: str


class InterviewIntelligenceEngine:
    """
    Generates evidence-based interview questions.

    The engine does not decide for the recruiter.
    It helps validate strengths, risks, uncertainties, and missing information.
    """

    def build_guide(self, report: CandidateReasoningReport) -> InterviewGuide:
        questions = []

        questions.extend(self._questions_from_strengths(report))
        questions.extend(self._questions_from_risks(report))
        questions.extend(self._questions_from_uncertainties(report))
        questions.extend(self._questions_from_missing_information(report))

        questions = self._deduplicate_questions(questions)

        return InterviewGuide(
            candidate_name=report.candidate_name,
            role_title=report.role_title,
            interview_focus=self._build_interview_focus(report),
            questions=questions[:8],
            closing_recommendation=(
                "Use this interview guide to validate evidence, clarify assumptions, "
                "and test whether the candidate's experience reflects real ownership, "
                "impact, and transferability to the target role."
            ),
        )

    def _build_interview_focus(self, report: CandidateReasoningReport) -> str:
        return (
            f"The interview should focus on validating the strongest positive signal "
            f"({report.strengths[0].title.lower()}), testing the main risk "
            f"({report.risks[0].title.lower()}), and clarifying uncertainty around "
            f"{report.uncertainties[0].title.lower()}."
        )

    def _questions_from_strengths(self, report: CandidateReasoningReport) -> List[InterviewQuestion]:
        questions = []

        for strength in report.strengths[:2]:
            evidence = strength.evidence[:3]

            questions.append(
                InterviewQuestion(
                    question=(
                        f"You have evidence suggesting '{strength.title}'. "
                        "Can you walk me through a concrete example where you personally contributed to this?"
                    ),
                    objective="Validate whether the documented strength reflects real ownership and impact.",
                    evidence_to_validate=evidence,
                    strong_answer_should_include=[
                        "Clear context and business problem",
                        "Candidate's personal role and level of ownership",
                        "Actions taken and decisions made",
                        "Measurable outcome or concrete impact",
                    ],
                    positive_signals=[
                        "Uses specific examples",
                        "Clarifies their own contribution",
                        "Provides measurable results",
                        "Explains trade-offs or constraints",
                    ],
                    red_flags=[
                        "Answers remain generic",
                        "Uses 'we' without clarifying personal role",
                        "Cannot provide outcomes",
                        "Describes exposure rather than ownership",
                    ],
                    follow_up_questions=[
                        "What exactly was your responsibility?",
                        "What was the measurable result?",
                        "What would have happened without your intervention?",
                    ],
                    evaluation_criteria=[
                        "Ownership",
                        "Impact",
                        "Specificity",
                        "Relevance to the role",
                    ],
                )
            )

        return questions

    def _questions_from_risks(self, report: CandidateReasoningReport) -> List[InterviewQuestion]:
        questions = []

        for risk in report.risks[:2]:
            questions.append(
                InterviewQuestion(
                    question=(
                        f"One potential concern is '{risk.title}'. "
                        "How would you address this point based on your actual experience?"
                    ),
                    objective="Assess whether the identified risk is a real gap or only a documentation gap.",
                    evidence_to_validate=risk.evidence[:4],
                    strong_answer_should_include=[
                        "Honest acknowledgement of the gap or ambiguity",
                        "Relevant transferable experience",
                        "Concrete examples",
                        "Learning ability or mitigation plan",
                    ],
                    positive_signals=[
                        "Acknowledges limits clearly",
                        "Provides adjacent experience",
                        "Shows learning agility",
                        "Explains how they would close the gap",
                    ],
                    red_flags=[
                        "Dismisses the concern without evidence",
                        "Overclaims experience",
                        "Cannot connect past experience to the role",
                    ],
                    follow_up_questions=[
                        "Can you give an example that proves this capability?",
                        "What support would you need to be successful?",
                        "How quickly could you become autonomous on this topic?",
                    ],
                    evaluation_criteria=[
                        "Self-awareness",
                        "Transferability",
                        "Learning agility",
                        "Risk mitigation",
                    ],
                )
            )

        return questions

    def _questions_from_uncertainties(self, report: CandidateReasoningReport) -> List[InterviewQuestion]:
        questions = []

        for uncertainty in report.uncertainties[:2]:
            questions.append(
                InterviewQuestion(
                    question=(
                        f"The analysis shows uncertainty around '{uncertainty.title}'. "
                        "Can you clarify this with a specific example?"
                    ),
                    objective="Reduce uncertainty by collecting concrete evidence during the interview.",
                    evidence_to_validate=uncertainty.evidence[:4],
                    strong_answer_should_include=[
                        "Specific example",
                        "Clear scope",
                        "Concrete responsibilities",
                        "Outcome or lesson learned",
                    ],
                    positive_signals=[
                        "Clarifies missing context",
                        "Gives precise facts",
                        "Quantifies scope or impact",
                    ],
                    red_flags=[
                        "Cannot clarify the uncertainty",
                        "Gives vague or theoretical answers",
                        "Avoids discussing responsibility or results",
                    ],
                    follow_up_questions=[
                        "What was the scope?",
                        "Who were the stakeholders?",
                        "What was the final outcome?",
                    ],
                    evaluation_criteria=[
                        "Clarity",
                        "Evidence quality",
                        "Credibility",
                        "Decision usefulness",
                    ],
                )
            )

        return questions

    def _questions_from_missing_information(self, report: CandidateReasoningReport) -> List[InterviewQuestion]:
        questions = []

        for missing in report.missing_information[:3]:
            questions.append(
                InterviewQuestion(
                    question=f"The CV does not clearly show this point: {missing} Can you clarify it?",
                    objective="Fill a specific information gap that affects confidence in the assessment.",
                    evidence_to_validate=[missing],
                    strong_answer_should_include=[
                        "Direct answer to the missing point",
                        "Concrete example",
                        "Scope, scale, or metrics where possible",
                    ],
                    positive_signals=[
                        "Provides factual details",
                        "Gives numbers or clear scope",
                        "Connects the answer to the role requirements",
                    ],
                    red_flags=[
                        "Cannot provide details",
                        "Gives only generic statements",
                        "Contradicts earlier evidence",
                    ],
                    follow_up_questions=[
                        "Can you quantify that?",
                        "Who was accountable for the final decision?",
                        "How was success measured?",
                    ],
                    evaluation_criteria=[
                        "Completeness",
                        "Evidence strength",
                        "Consistency",
                        "Role relevance",
                    ],
                )
            )

        return questions

    def _deduplicate_questions(self, questions: List[InterviewQuestion]) -> List[InterviewQuestion]:
        seen = set()
        unique = []

        for question in questions:
            key = question.question.lower().strip()
            if key not in seen:
                unique.append(question)
                seen.add(key)

        return unique
