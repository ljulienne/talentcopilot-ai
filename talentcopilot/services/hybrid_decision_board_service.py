from dataclasses import dataclass

from talentcopilot.hybrid_matching.decision_board_engine import HybridDecisionBoardEngine
from talentcopilot.hybrid_matching.decision_board_models import HybridDecisionBoard
from talentcopilot.llm_extraction.real_ranking import (
    LLMCandidateTextInput,
    LLMRealRankingInput,
    LLMRealRankingPipeline,
)


@dataclass
class HybridDecisionBoardDemo:
    board: HybridDecisionBoard


class HybridDecisionBoardService:
    def build_from_ranking_output(self, ranking_output) -> HybridDecisionBoard:
        return HybridDecisionBoardEngine().build_from_ranking_output(ranking_output)

    def run_demo(self) -> HybridDecisionBoardDemo:
        ranking_output = LLMRealRankingPipeline().run(
            LLMRealRankingInput(
                job_filename="job.txt",
                job_text="HRIS Manager. Required skills: HRIS, Project Management, Time Management, Reporting, Payroll.",
                candidates=[
                    LLMCandidateTextInput(
                        "vincent.txt",
                        "Vincent BLAKOE\n13 years experience. SIRH, Workday, OCTIME, Business Objects. Improved adoption by 35%. Led HRIS transformation.",
                    ),
                    LLMCandidateTextInput(
                        "loretta.txt",
                        "LORETTA DANIELSON, MBA, SPHR\nHuman Resources Director. HRIS, Leadership, Change Management. Managed 45 HR professionals.",
                    ),
                    LLMCandidateTextInput(
                        "junior.txt",
                        "Junior HR Assistant\nRecruitment coordination, onboarding, Excel reporting.",
                    ),
                ],
            )
        )
        return HybridDecisionBoardDemo(board=self.build_from_ranking_output(ranking_output))
