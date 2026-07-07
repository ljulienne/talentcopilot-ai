from talentcopilot.ai.enterprise_pipeline import EnterprisePipeline
from talentcopilot.models.recruitment_session import SessionStatus


def test_enterprise_pipeline_creates_ranked_session():
    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
    }

    candidates = [
        {"name": "Bob", "skills": ["Excel"]},
        {
            "name": "Alice",
            "skills": ["Project Management", "Stakeholder Management"],
            "achievements": ["Led transformation project"],
        },
    ]

    session = EnterprisePipeline().run(job, candidates)

    assert session.status == SessionStatus.COMPLETED
    assert session.candidate_count == 2
    assert len(session.analyses) == 2
    assert session.ranked_analyses[0].candidate_name == "Alice"
    assert session.ranked_analyses[0].rank == 1


def test_enterprise_pipeline_handles_empty_candidates():
    session = EnterprisePipeline().run({"title": "Role"}, [])

    assert session.status == SessionStatus.COMPLETED
    assert session.candidate_count == 0
    assert session.analyses == []
