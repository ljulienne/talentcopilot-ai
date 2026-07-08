from dataclasses import dataclass, field
from typing import List

@dataclass
class HybridInterviewQuestion:
    focus_area: str
    question: str
    follow_up: str
    strong_signal: str
    red_flag: str
    evaluation_criterion: str

@dataclass
class HybridInterviewPlan:
    candidate_name: str
    role_title: str
    questions: List[HybridInterviewQuestion] = field(default_factory=list)

    @property
    def total_questions(self) -> int:
        return len(self.questions)
