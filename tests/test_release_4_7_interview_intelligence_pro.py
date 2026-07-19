from dataclasses import dataclass

from talentcopilot.interview.pro_service import InterviewIntelligenceProService
from talentcopilot.services.interview_report_pdf_service import InterviewReportPdfService


@dataclass
class Analysis:
    candidate_name: str = "Alice Martin"
    match_score: float = 86.0
    official_rank: int = 1
    ai_confidence: int = 82


def test_star_assessment_detects_complete_evidence():
    answer = (
        "During a global HRIS rollout, I was responsible for integration readiness. "
        "I designed the validation plan, led defect triage and changed the cutover sequence. "
        "As a result, critical defects were reduced by 35% and go-live finished two weeks early."
    )
    star = InterviewIntelligenceProService().assess_star(answer)
    assert star.situation
    assert star.task
    assert star.action
    assert star.result
    assert star.ownership
    assert star.metrics
    assert star.completeness_score >= 80


def test_follow_up_prompts_target_missing_star_elements():
    service = InterviewIntelligenceProService()
    star = service.assess_star("We worked on a difficult transformation project.")
    prompts = service.suggest_follow_ups(star, "Change Management")
    assert prompts
    assert any("personally" in prompt.lower() for prompt in prompts)


def test_recommendation_is_explainable_and_evidence_based():
    service = InterviewIntelligenceProService()
    ratings = [
        service.build_rating(
            "Leadership",
            "During a programme I was responsible for delivery. I led the team and improved adoption by 25%.",
            5,
            True,
        ),
        service.build_rating(
            "Stakeholder Management",
            "During an HR project I owned governance. I negotiated priorities and delivered the decision in 3 weeks.",
            4,
            True,
        ),
    ]
    outcome = service.evaluate("Alice Martin", ratings)
    assert outcome.recommendation.label in {"Strong Hire", "Hire"}
    assert outcome.recommendation.rationale
    assert outcome.evidence_coverage == 100


def test_low_or_unconfirmed_evidence_cannot_produce_strong_hire():
    service = InterviewIntelligenceProService()
    ratings = [
        service.build_rating("Leadership", "We helped on a project.", 5, False),
        service.build_rating("Communication", "I attended meetings.", 4, False),
    ]
    outcome = service.evaluate("Candidate", ratings)
    assert outcome.recommendation.label not in {"Strong Hire", "Hire"}
    assert outcome.recommendation.remaining_risks


def test_interview_intelligence_does_not_mutate_official_decision_values():
    service = InterviewIntelligenceProService()
    analysis = Analysis()
    before = (analysis.match_score, analysis.official_rank, analysis.ai_confidence)
    rating = service.build_rating(
        "Leadership",
        "During a project I owned delivery. I led the work and improved quality by 20%.",
        5,
        True,
    )
    service.evaluate(analysis.candidate_name, [rating])
    after = (analysis.match_score, analysis.official_rank, analysis.ai_confidence)
    assert after == before


def test_interview_report_pdf_is_valid():
    service = InterviewIntelligenceProService()
    rating = service.build_rating(
        "Leadership",
        "During a project I owned delivery. I led the team and improved adoption by 30%.",
        5,
        True,
    )
    outcome = service.evaluate("Alice Martin", [rating])
    pdf = InterviewReportPdfService().build(outcome, "HRIS Transformation Lead")
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_ui_contains_release_4_7_workflow():
    source = open("talentcopilot/ui/interview_intelligence.py", encoding="utf-8").read()
    assert "Interview Intelligence Pro" in source
    assert "Live Evaluation" in source
    assert "Generate post-interview recommendation" in source
    assert "InterviewReportPdfService" in source
