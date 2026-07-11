from __future__ import annotations

from .models import ExecutiveQuestion, QuestionDomain


QUESTIONS: tuple[ExecutiveQuestion, ...] = (
    ExecutiveQuestion(
        question_id="HR-RISK-001",
        title="What are the main organizational risks?",
        domain=QuestionDomain.RISK,
        description="Prioritize the most material organizational risks and recommended actions.",
        required_engines=("Knowledge", "Organization Graph", "Collaboration", "Skills", "Workforce"),
        keywords=("risk", "risks", "priority", "priorities", "urgent", "attention"),
        follow_up_ids=("HR-SKILL-001", "HR-SUCCESSION-001", "HR-ORG-001"),
    ),
    ExecutiveQuestion(
        question_id="HR-SKILL-001",
        title="Which skills are most critical?",
        domain=QuestionDomain.SKILLS,
        description="Surface rare, concentrated or strategically missing skills.",
        required_engines=("Skills", "Knowledge"),
        keywords=("skill", "skills", "rare", "critical skill", "gap", "capability"),
        follow_up_ids=("HR-HIRE-001", "HR-SUCCESSION-001"),
    ),
    ExecutiveQuestion(
        question_id="HR-SUCCESSION-001",
        title="Where are succession plans insufficient?",
        domain=QuestionDomain.SUCCESSION,
        description="Identify roles or people with insufficient succession coverage.",
        required_engines=("Workforce", "Knowledge", "Skills"),
        keywords=("succession", "successor", "replacement", "backup", "critical employee"),
        follow_up_ids=("HR-WORKFORCE-001", "HR-HIRE-001"),
    ),
    ExecutiveQuestion(
        question_id="HR-WORKFORCE-001",
        title="Which workforce continuity risks require action?",
        domain=QuestionDomain.WORKFORCE,
        description="Prioritize continuity risks linked to departures and weak internal coverage.",
        required_engines=("Workforce", "Skills", "Knowledge"),
        keywords=("workforce", "departure", "leave", "continuity", "retirement", "attrition"),
        follow_up_ids=("HR-SUCCESSION-001", "HR-HIRE-001"),
    ),
    ExecutiveQuestion(
        question_id="HR-ORG-001",
        title="Which departments need attention?",
        domain=QuestionDomain.COLLABORATION,
        description="Identify weak collaboration, silos and critical organizational bridges.",
        required_engines=("Collaboration", "Organization Graph"),
        keywords=("department", "departments", "team", "teams", "silo", "collaboration", "bridge"),
        follow_up_ids=("HR-RISK-001", "HR-WORKFORCE-001"),
    ),
    ExecutiveQuestion(
        question_id="HR-HIRE-001",
        title="Which hiring priorities should be addressed first?",
        domain=QuestionDomain.RECRUITMENT,
        description="Convert skill and workforce gaps into recruitment priorities.",
        required_engines=("Skills", "Workforce"),
        keywords=("hire", "hiring", "recruit", "recruitment", "vacancy", "headcount"),
        follow_up_ids=("HR-SKILL-001", "HR-WORKFORCE-001"),
    ),
    ExecutiveQuestion(
        question_id="HR-OVERVIEW-001",
        title="What should leadership prioritize this week?",
        domain=QuestionDomain.OVERVIEW,
        description="Provide a concise executive overview of the most important current actions.",
        required_engines=("Knowledge", "Organization Graph", "Collaboration", "Skills", "Workforce"),
        keywords=("overview", "this week", "today", "leadership", "executive", "summary"),
        follow_up_ids=("HR-RISK-001", "HR-SKILL-001", "HR-SUCCESSION-001"),
    ),
)


class QuestionCatalog:
    def __init__(self, questions: tuple[ExecutiveQuestion, ...] = QUESTIONS) -> None:
        self.questions = questions
        self._by_id = {item.question_id: item for item in questions}

    def get(self, question_id: str) -> ExecutiveQuestion | None:
        return self._by_id.get(question_id)

    def all(self) -> tuple[ExecutiveQuestion, ...]:
        return self.questions

    def follow_ups(self, question: ExecutiveQuestion) -> tuple[ExecutiveQuestion, ...]:
        return tuple(
            item
            for question_id in question.follow_up_ids
            if (item := self.get(question_id)) is not None
        )
