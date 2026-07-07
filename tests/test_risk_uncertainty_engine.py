from talentcopilot.ai.evidence_quality_engine import EvidenceQualityEngine
from talentcopilot.ai.uncertainty_engine import UncertaintyEngine
from talentcopilot.ai.risk_engine import RiskEngine


def test_uncertainty_and_risk_detect_missing_evidence():
    candidate = {
        "name": "Bob",
        "skills": ["Excel"],
        "achievements": ["Prepared monthly reports"],
    }

    job = {
        "title": "Data Engineer",
        "required_skills": ["Python", "SQL"],
    }

    evidence_quality = EvidenceQualityEngine().assess(candidate, job)
    uncertainty = UncertaintyEngine().assess(evidence_quality)
    risk = RiskEngine().assess(evidence_quality, uncertainty)

    assert uncertainty.overall_uncertainty >= 0
    assert risk.overall_risk_level in {"Low", "Medium", "High"}
    assert len(risk.risks) >= 1
