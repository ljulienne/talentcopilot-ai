from dataclasses import dataclass

from talentcopilot.interview_intelligence_v2.interview_engine import InterviewIntelligenceEngine
from talentcopilot.interview_intelligence_v2.models import InterviewQuestionSet
from talentcopilot.services.real_ranking_demo_service import RealRankingDemoService


@dataclass
class InterviewIntelligenceDemo:
    question_set: InterviewQuestionSet


class InterviewIntelligenceDemoService:
    def run_demo(self) -> InterviewIntelligenceDemo:
        ranking = RealRankingDemoService().run_demo().output
        top = ranking.ranked_candidates[0]
        profile = top.matching_output.decision_output.profile
        question_set = InterviewIntelligenceEngine().generate(profile)
        return InterviewIntelligenceDemo(question_set=question_set)
