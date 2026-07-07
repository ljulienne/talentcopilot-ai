from talentcopilot.services.demo_session_factory import (
    create_demo_recruitment_session,
    demo_candidates,
    demo_job,
)


def test_demo_session_factory_creates_analyzed_session():
    session = create_demo_recruitment_session()

    assert session.role_title == demo_job()["title"]
    assert session.candidate_count == len(demo_candidates())
    assert session.analyzed_count == len(demo_candidates())
    assert session.ranked_analyses[0].rank == 1
