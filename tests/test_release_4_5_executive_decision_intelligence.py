from talentcopilot.models.candidate_intelligence import CandidateIntelligenceSnapshot
from talentcopilot.models.candidate_workspace import CandidateSkill, CandidateWorkspaceReport
from talentcopilot.reports.executive_decision_pdf import generate_executive_decision_pdf
from talentcopilot.services.executive_decision_intelligence_service import ExecutiveDecisionIntelligenceService


def _report(score=86, rank=1, confidence=84):
    return CandidateWorkspaceReport(candidate_name='Louis', candidate_id='louis', rank=rank, match_score=score, score_breakdown={'confidence': confidence}, recommendation='Proceed', executive_summary='Existing summary', skills=[CandidateSkill('HRIS',88,'evidence'), CandidateSkill('API Integration',82,'evidence')], evidence=[], risks=[], interview_focus=['Validate global rollout ownership.'])

def _intel(confidence=84):
    return CandidateIntelligenceSnapshot(candidate_name='Louis', mission_fit=86, evidence_coverage=80, decision_confidence=confidence, potential_signal=78, recommendation='Proceed', recommendation_explanation='Supported', strengths=('HRIS transformation','API Integration'), risks=(), missing_evidence=(), interview_strategy=('Validate global rollout ownership.','Confirm measurable outcomes.'), evidence_summary='5 usable evidence items.')

def test_release_4_5_preserves_official_values():
    brief=ExecutiveDecisionIntelligenceService().build(_report(),_intel())
    assert brief.official_match_score==86
    assert brief.official_rank==1
    assert brief.ai_confidence==84

def test_release_4_5_builds_executive_decision_outputs():
    brief=ExecutiveDecisionIntelligenceService().build(_report(),_intel())
    assert brief.recommendation=='Strong Hire'
    assert brief.business_impact=='High'
    assert brief.expected_ramp_up in {'Immediate to 1 month','1–2 months'}
    assert len(brief.risks)>=3
    assert brief.interview_priorities

def test_release_4_5_low_fit_is_not_prioritized():
    brief=ExecutiveDecisionIntelligenceService().build(_report(score=25,rank=4,confidence=71),_intel(71))
    assert brief.recommendation=='Do not prioritize'
    assert brief.expected_ramp_up=='Long ramp-up'

def test_release_4_5_pdf_is_valid():
    data=generate_executive_decision_pdf(ExecutiveDecisionIntelligenceService().build(_report(),_intel()))
    assert data.startswith(b'%PDF')
    assert len(data)>1000

def test_release_4_5_ui_exposes_advisor_and_pdf():
    source=open('talentcopilot/ui/candidate_workspace.py').read()
    assert 'AI Executive Advisor' in source
    assert 'Download Executive Decision Brief (PDF)' in source
