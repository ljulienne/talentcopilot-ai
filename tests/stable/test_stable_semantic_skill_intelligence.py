from talentcopilot.semantic_intelligence.skill_graph import SkillGraph
from talentcopilot.semantic_intelligence.skill_matcher import SemanticSkillMatcher


def test_skill_graph_normalizes_french_and_english_aliases():
    graph = SkillGraph()

    assert graph.normalize("SIRH") == "HRIS"
    assert graph.normalize("gestion des temps") == "Time Management"
    assert graph.normalize("Business Objects") == "Reporting"


def test_semantic_skill_matcher_exact_and_related_matches():
    report = SemanticSkillMatcher().compare(
        required_skills=["HRIS", "Time Management", "Reporting"],
        candidate_skills=["Workday", "OCTIME", "Business Objects"],
    )

    assert report.average_score >= 70
    assert report.covered_skills == 3
    assert all(match.score >= 70 for match in report.matches)


def test_semantic_skill_matcher_missing_skill():
    report = SemanticSkillMatcher().compare(
        required_skills=["Payroll", "Leadership"],
        candidate_skills=["Graphic Design"],
    )

    assert report.average_score < 50
    assert "Payroll" in report.missing_skills
