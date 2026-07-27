from dataclasses import dataclass
from pathlib import Path

from talentcopilot.ui.competency_star import (
    build_competency_star_data,
    build_competency_star_figure,
)


@dataclass
class Competency:
    name: str
    confidence: int


def competencies():
    return [
        Competency("Leadership", 88),
        Competency("Stakeholder Management", 68),
        Competency("Change Management", 38),
        Competency("HRIS", 76),
    ]


def test_pre_interview_profile_uses_evidence_confidence():
    data = build_competency_star_data(
        competencies()
    )

    assert data["labels"] == [
        "Leadership",
        "Stakeholder Management",
        "Change Management",
        "HRIS",
    ]

    assert data["pre_interview"] == [
        88,
        68,
        38,
        76,
    ]

    assert data["has_live_evidence"] is False


def test_live_profile_uses_recruiter_rating():
    data = build_competency_star_data(
        competencies(),
        [
            {
                "competency": "Leadership",
                "score": 5,
                "evidence_confirmed": True,
                "answer": "I led the programme.",
                "notes": "",
            },
            {
                "competency": "Stakeholder Management",
                "score": 4,
                "evidence_confirmed": False,
                "answer": "I negotiated priorities.",
                "notes": "",
            },
        ],
    )

    assert data["has_live_evidence"] is True
    assert data["live_interview"][0] == 100
    assert data["live_interview"][1] == 80
    assert data["live_status"][0] == "Confirmed"
    assert data["live_status"][1] == "Captured"


def test_default_slider_does_not_create_false_live_result():
    data = build_competency_star_data(
        competencies(),
        [
            {
                "competency": "Leadership",
                "score": 3,
                "evidence_confirmed": False,
                "answer": "",
                "notes": "",
            },
        ],
    )

    assert data["has_live_evidence"] is False
    assert data["live_interview"][0] == 88


def test_radar_contains_one_or_two_profiles():
    pre_data = build_competency_star_data(
        competencies()
    )

    pre_figure = build_competency_star_figure(
        pre_data
    )

    assert len(pre_figure.data) == 1

    live_data = build_competency_star_data(
        competencies(),
        [
            {
                "competency": "Leadership",
                "score": 5,
                "evidence_confirmed": True,
                "answer": "Evidence",
                "notes": "",
            },
        ],
    )

    live_figure = build_competency_star_figure(
        live_data
    )

    assert len(live_figure.data) == 2


def test_active_star_renderer_integrates_radar():
    source = Path(
        'talentcopilot/ui/interview_intelligence.py'
    ).read_text(encoding="utf-8")

    assert "render_competency_star" in source
    assert "live_assessments.append" in source
    assert "Competency Star" in source
    assert "competency-star:" in source


def test_component_does_not_modify_official_decision_fields():
    source = Path(
        "talentcopilot/ui/competency_star.py"
    ).read_text(encoding="utf-8")

    forbidden = [
        "official_rank =",
        "match_score =",
        "official_match_score =",
        "ranking_score =",
        "ai_confidence =",
    ]

    for expression in forbidden:
        assert expression not in source
