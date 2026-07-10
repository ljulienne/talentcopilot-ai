from talentcopilot.organization_intelligence import CollaborationRecord, OrganizationIntelligenceService


def test_demo_diagnostic_is_explainable():
    service = OrganizationIntelligenceService()
    diagnostic = service.analyze(service.demo_records())

    assert diagnostic.record_count == 9
    assert set(diagnostic.departments) == {"Finance", "HR", "IT", "Operations"}
    assert diagnostic.total_weight > diagnostic.cross_department_weight > 0
    assert diagnostic.connectors
    assert diagnostic.executive_summary
    assert diagnostic.recommendations


def test_empty_diagnostic_is_safe():
    diagnostic = OrganizationIntelligenceService().analyze([])
    assert diagnostic.record_count == 0
    assert diagnostic.departments == []
    assert diagnostic.recommendations


def test_low_collaboration_department_is_ranked_first():
    rows = [
        CollaborationRecord("A", "HR", "B", "HR", 20),
        CollaborationRecord("A", "HR", "C", "IT", 1),
        CollaborationRecord("C", "IT", "D", "Finance", 10),
    ]
    diagnostic = OrganizationIntelligenceService().analyze(rows)
    assert diagnostic.department_insights[0].department == "HR"
