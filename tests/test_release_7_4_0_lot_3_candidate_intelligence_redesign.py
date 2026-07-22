from pathlib import Path

from talentcopilot.models.candidate_workspace import CandidateWorkspaceReport
from talentcopilot.services.candidate_intelligence_view_service import CandidateIntelligenceViewService
from talentcopilot.services.candidate_intelligence import CandidateIntelligenceService


SOURCE = Path('talentcopilot/ui/candidate_workspace.py').read_text(encoding='utf-8')


def _report():
    return CandidateWorkspaceReport(
        candidate_name='Candidate One',
        candidate_id='c1',
        rank=2,
        match_score=64.0,
        recommendation='Proceed with validation',
        executive_summary='Relevant profile with evidence to validate.',
        skills=[],
    )


def test_candidate_intelligence_uses_decision_first_structure():
    assert 'Decision snapshot' in SOURCE
    assert 'Prepare interview →' in SOURCE
    assert 'render_recruitment_workflow_shell' not in SOURCE
    assert 'current_page="Candidate Intelligence"' in SOURCE


def test_candidate_intelligence_reduces_primary_tabs_and_uses_disclosure():
    assert '"Competencies",\n        "Evidence & validation",\n        "Decision governance"' in SOURCE
    assert 'Open full dynamic competency matrix' in SOURCE
    assert 'AI Executive Advisor' in SOURCE
    assert 'Executive Decision Center' in SOURCE


def test_candidate_intelligence_routes_to_interview_without_recalculating_score():
    assert 'request_page(\n                "Interview Intelligence"' in SOURCE
    forbidden = ('match_score =', '.match_score =', 'rank = report.rank +')
    render_source = SOURCE[SOURCE.index('def render_candidate_workspace():'):]
    assert not any(token in render_source for token in forbidden)


def test_decision_view_preserves_official_score_and_rank():
    report = _report()
    intelligence = CandidateIntelligenceService().build(report)
    brief = CandidateIntelligenceViewService().build(report, intelligence)
    assert brief.official_match_score == 64.0
    assert brief.official_rank == 2
    assert report.match_score == 64.0
    assert report.rank == 2
