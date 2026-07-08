from talentcopilot.interview_intelligence_v2.evidence_gap_engine import EvidenceGapEngine
from talentcopilot.interview_intelligence_v2.interview_engine import InterviewIntelligenceEngine
from talentcopilot.services.real_ranking_demo_service import RealRankingDemoService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_evidence_gap_engine_detects_gaps():
    ranking = RealRankingDemoService().run_demo().output
    profile = ranking.ranked_candidates[-1].matching_output.decision_output.profile

    gaps = EvidenceGapEngine().detect(profile)

    assert gaps
    assert any(gap.area in {"Role fit", "Hiring risk", "Decision confidence", "Final validation"} for gap in gaps)


def test_interview_intelligence_generates_questions():
    ranking = RealRankingDemoService().run_demo().output
    profile = ranking.ranked_candidates[0].matching_output.decision_output.profile

    question_set = InterviewIntelligenceEngine().generate(profile)

    assert question_set.candidate_name == profile.candidate_name
    assert question_set.questions
    assert question_set.evidence_gaps
    assert question_set.summary


def test_interview_intelligence_ui_imports():
    module = __import__("talentcopilot.ui.interview_intelligence", fromlist=["render_interview_intelligence"])
    assert hasattr(module, "render_interview_intelligence")


def test_interview_intelligence_navigation():
    page = get_page_by_label("Interview Intelligence")
    assert page is not None
    assert page.module == "talentcopilot.ui.interview_intelligence"
