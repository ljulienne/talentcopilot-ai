from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees
from talentcopilot.workforce_intelligence import WorkforceScenarioEngine, successors_dataframe


def _employees():
    return dataframe_to_employees(demo_dataframe())


def test_departure_scenario_returns_explainable_impact():
    report = WorkforceScenarioEngine().analyze_departure(_employees(), "E001")
    assert report.scenario_type == "Departure"
    assert report.impact.employee_name == "Marie Dupont"
    assert report.impact.risk_score >= 0
    assert report.impact.risk_level in {"Low", "Medium", "High", "Critical"}
    assert report.impact.insights
    assert report.impact.recommendations


def test_departure_scenario_identifies_successors():
    report = WorkforceScenarioEngine().analyze_departure(_employees(), "E001")
    names = [item.name for item in report.impact.successor_candidates]
    assert "Sofia Martin" in names or "Jean Morel" in names or "Thomas Lee" in names
    if report.impact.successor_candidates:
        assert report.impact.successor_candidates[0].readiness_score >= 0


def test_successor_export_is_available():
    report = WorkforceScenarioEngine().analyze_departure(_employees(), "E001")
    df = successors_dataframe(report)
    assert set(["name", "readiness_score", "matched_skills"]).issubset(df.columns)


def test_unknown_employee_is_rejected():
    try:
        WorkforceScenarioEngine().analyze_departure(_employees(), "UNKNOWN")
    except ValueError as exc:
        assert "Unknown employee_id" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
