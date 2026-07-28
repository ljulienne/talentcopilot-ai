from pathlib import Path
from types import SimpleNamespace

from talentcopilot.interview.pro_service import InterviewIntelligenceProService
from talentcopilot.ui.competency_star import build_competency_star_data


def _competency(name: str, *, origin: str = "job_requirement", level: float = 3.0):
    return SimpleNamespace(
        competency_name=name,
        required_level=4.0 if origin == "job_requirement" else 0.0,
        ai_estimated_level=2.5 if origin == "job_requirement" else 0.0,
        interviewer_level=level if origin == "interview_added" else None,
        validation_status="To validate",
        origin=origin,
        is_active=True,
    )


def test_interview_added_competency_is_never_hidden_by_seven_axis_limit():
    competencies = [_competency(f"Role competency {index}") for index in range(1, 8)]
    competencies.append(
        _competency("Vendor Management", origin="interview_added", level=4.0)
    )

    data = build_competency_star_data(competencies)

    assert data["displayed_count"] == 8
    assert data["labels"][-1] == "Vendor Management"
    assert data["post_interview"][-1] == 80
    assert data["interview_added_count"] == 1


def test_dense_radar_keeps_all_active_competencies_and_reports_density():
    competencies = [_competency(f"Competency {index}") for index in range(1, 12)]

    data = build_competency_star_data(competencies)

    assert len(data["labels"]) == 11
    assert data["displayed_count"] == 11
    assert data["is_dense"] is True


def test_star_assessment_understands_complete_french_evidence():
    answer = (
        "Pendant le déploiement d'un SIRH mondial, j'étais responsable de la préparation "
        "des interfaces. J'ai conçu le plan de validation, piloté la résolution des anomalies "
        "et décidé de modifier le calendrier de bascule. Le résultat a été une réduction de "
        "35 % des anomalies critiques et une mise en production deux semaines plus tôt."
    )

    star = InterviewIntelligenceProService().assess_star(answer)

    assert star.situation
    assert star.task
    assert star.action
    assert star.result
    assert star.ownership
    assert star.metrics
    assert star.completeness_score >= 80


def test_star_assessment_handles_french_curly_apostrophes_and_accents():
    answer = (
        "Lors d’une transformation RH, j’étais chargé de l’adoption. "
        "J’ai piloté les ateliers et augmenté l’adoption de 25 %."
    )

    star = InterviewIntelligenceProService().assess_star(answer)

    assert star.situation
    assert star.task
    assert star.action
    assert star.result
    assert star.ownership
    assert star.metrics
    assert star.completeness_score >= 80


def test_empty_answer_is_shown_as_not_assessed_in_the_ui():
    source = Path("talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")

    assert "STAR evidence completeness: not assessed" in source
    assert "if answer.strip():" in source
