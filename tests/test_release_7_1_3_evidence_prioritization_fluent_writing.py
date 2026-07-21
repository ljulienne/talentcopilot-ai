from types import SimpleNamespace

from talentcopilot.recruitment.mission.narrative import (
    candidate_assessment,
    executive_summary,
    recruiter_reasoning,
)
from talentcopilot.recruitment_reasoning.engine import RecruitmentReasoningEngine
from talentcopilot.recruitment_reasoning.models import CriterionAssessment, MissionCriterion


def _candidate(name, rank, score, rationale, recommendation, strengths=(), focuses=()):
    return SimpleNamespace(
        name=name,
        rank=rank,
        match_score=score,
        rationale=rationale,
        recommendation=recommendation,
        strengths=tuple(strengths),
        risks=(),
        validation_focus=tuple(focuses),
    )


def test_eligibility_evidence_is_not_prioritized_over_capabilities():
    engine = RecruitmentReasoningEngine()
    tenure = CriterionAssessment(
        criterion=MissionCriterion(
            key="minimum_experience",
            label="Minimum 10 years of relevant experience",
            category="experience",
            weight=0.2,
            mandatory=True,
            aliases=["10"],
        ),
        evidence_level="direct",
        evidence_score=1.0,
        contribution=20.0,
        evidence=["17 years evidenced against 10 required"],
    )
    transformation = CriterionAssessment(
        criterion=MissionCriterion(
            key="skill_change_management",
            label="Change Management",
            category="capability",
            weight=0.1,
            mandatory=False,
            aliases=["change management"],
        ),
        evidence_level="direct",
        evidence_score=1.0,
        contribution=10.0,
        evidence=["Direct evidence: change management"],
    )
    ranked = sorted([tenure, transformation], key=engine._evidence_priority, reverse=True)
    assert ranked[0].criterion.key == "skill_change_management"


def test_candidate_assessment_prioritizes_projects_tools_and_ownership_over_tenure():
    candidate = _candidate(
        "Louis Julienne",
        1,
        84,
        "Louis Julienne is a strong, credible match. The principal decision uncertainties concern SAP and Process Design.",
        "Strong Hire",
        strengths=(
            "The profile clearly meets the required level of seniority (17 years evidenced against 10 required), supporting role readiness without being a differentiator on its own.",
            "Led a multi-country HR transformation and stakeholder governance programme.",
            "Direct evidence of HRIS implementation supports the candidate's capability in Core platform deployment.",
        ),
    )
    text = candidate_assessment(candidate)
    assert "multi-country HR transformation" in text
    assert "HRIS implementation" in text
    assert "17 years" not in text
    assert "more decision-relevant than simply meeting" in text


def test_recruiter_reasoning_is_fluent_and_does_not_repeat_score_or_robotic_labels():
    candidate = _candidate(
        "Louis Julienne",
        1,
        84,
        "Louis Julienne is a strong, credible match. The official Mission Fit is 84%, with 96% evidence confidence. The most compelling evidence comes from direct evidence of HRIS implementation. The principal decision uncertainties concern Tool Sap and Process Design.",
        "Strong Hire",
        strengths=("Led an HR technology transformation across several countries.",),
        focuses=("Establish whether SAP experience included direct system ownership",),
    )
    paragraphs = recruiter_reasoning(candidate)
    joined = " ".join(paragraphs)
    assert joined.count("84%") == 1
    assert "96% evidence confidence" not in joined
    assert "Tool Sap" not in joined
    assert "SAP" in joined
    assert "17 years evidenced" not in joined
    assert "The practical implication" in joined


def test_executive_summary_explicitly_avoids_tenure_as_the_primary_differentiator():
    lead = _candidate(
        "Louis Julienne",
        1,
        84,
        "The principal decision uncertainty concerns SAP.",
        "Strong Hire",
        strengths=(
            "17 years of experience",
            "Led a global HR transformation programme",
        ),
    )
    alternative = _candidate("Vincent Blakoe", 2, 80, "", "Interview")
    text = executive_summary("HRIS Manager", (lead, alternative))
    assert "global HR transformation programme" in text
    assert "rather than tenure alone" in text
    assert "17 years" not in text


def test_rationale_uses_differentiators_before_eligibility():
    engine = RecruitmentReasoningEngine()
    capability = CriterionAssessment(
        criterion=MissionCriterion("integration", "Systems integration / interfaces", "capability", 0.4),
        evidence_level="direct",
        evidence_score=1.0,
        contribution=40.0,
        evidence=["Direct evidence: systems integration"],
    )
    tenure = CriterionAssessment(
        criterion=MissionCriterion("minimum_experience", "Minimum 10 years of relevant experience", "experience", 0.3, True, ["10"]),
        evidence_level="direct",
        evidence_score=1.0,
        contribution=30.0,
        evidence=["17 years evidenced against 10 required"],
    )
    strengths = [engine._strength_statement(capability), engine._strength_statement(tenure)]
    text = engine._rationale(
        "Candidate",
        84,
        "Strong Hire",
        "Low",
        90,
        strengths,
        [],
        [capability, tenure],
    )
    differentiator_pos = text.find("systems integration")
    tenure_pos = text.find("required level of seniority")
    assert differentiator_pos != -1
    assert tenure_pos == -1 or differentiator_pos < tenure_pos
