from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ui.components.reasoning_cards import render_reasoning_report


def test_render_reasoning_report_is_callable():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Change Management"],
        "years_experience": 8,
    }

    job = {
        "title": "Transformation Manager",
        "required_skills": ["Project Management", "Change Management"],
        "years_experience": 5,
    }

    engine = ReasoningEngine()
    report = engine.build_report(candidate=candidate, job=job)

    assert callable(render_reasoning_report)
    assert report.executive_summary
