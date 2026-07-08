def test_decision_and_governance_cards_import():
    imports = [
        ("talentcopilot.ui.decision_cards", "render_decision_intelligence_card"),
        ("talentcopilot.ui.decision_cards", "render_decision_summary_badge"),
        ("talentcopilot.ui.governance_cards", "render_governance_card"),
        ("talentcopilot.services.demo_session_factory", "DemoSessionFactory"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)


def test_demo_session_factory_lightweight_methods():
    from talentcopilot.services.demo_session_factory import DemoSessionFactory

    assert DemoSessionFactory.demo_job()["title"] == "Transformation Lead"
    assert len(DemoSessionFactory.demo_candidates()) >= 1
