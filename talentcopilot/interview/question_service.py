from talentcopilot.interview.models import InterviewCompetency, InterviewQuestion


class InterviewQuestionService:
    def build(self, competencies: list[InterviewCompetency]) -> list[InterviewQuestion]:
        target_competencies = [c for c in competencies if c.validate_in_interview]
        if not target_competencies:
            target_competencies = competencies[:3]

        questions = []
        for competency in target_competencies[:6]:
            name = competency.name
            questions.append(
                InterviewQuestion(
                    competency=name,
                    question=f"Tell me about a concrete situation where you demonstrated {name}.",
                    objective=f"Validate the candidate's real depth in {name}.",
                    expected_evidence=[
                        "Specific context",
                        "Candidate's personal role",
                        "Actions taken",
                        "Measurable outcome",
                    ],
                    positive_signals=[
                        "Clear ownership",
                        "Structured answer",
                        "Quantified impact",
                        "Reflection on lessons learned",
                    ],
                    warning_signals=[
                        "Vague example",
                        "No measurable outcome",
                        "No clear personal contribution",
                    ],
                    follow_ups=[
                        "What was the most difficult trade-off?",
                        "How did stakeholders react?",
                        "What would you do differently now?",
                    ],
                )
            )

        return questions
