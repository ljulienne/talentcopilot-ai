from talentcopilot.analytics import recruitment_statistics as stats


def test_workspace_statistics_with_no_recruitments(monkeypatch):
    monkeypatch.setattr(stats, "list_recruitments", lambda: [])

    result = stats.get_workspace_statistics()

    assert result["total_recruitments"] == 0
    assert result["complete_recruitments"] == 0
    assert result["draft_recruitments"] == 0
    assert result["total_candidates"] == 0
    assert result["average_match"] == 0
    assert result["top_candidate"] is None
    assert result["recent_recruitments"] == []


def test_workspace_statistics_with_recruitments(monkeypatch):
    summaries = [
        {"id": "REC-001", "title": "HRIS Manager", "candidate_count": 2},
        {"id": "REC-002", "title": "Payroll Manager", "candidate_count": 0},
    ]

    recruitments = {
        "REC-001": {
            "id": "REC-001",
            "title": "HRIS Manager",
            "analysis_batch": {
                "results": [
                    {
                        "candidate": {"name": "Emma Martin"},
                        "match_result": {
                            "overall_score": 92,
                            "confidence_score": 95,
                        },
                    },
                    {
                        "candidate": {"name": "John Smith"},
                        "match_result": {
                            "overall_score": 78,
                            "confidence_score": 85,
                        },
                    },
                ]
            },
        },
        "REC-002": {
            "id": "REC-002",
            "title": "Payroll Manager",
            "analysis_batch": {"results": []},
        },
    }

    monkeypatch.setattr(stats, "list_recruitments", lambda: summaries)
    monkeypatch.setattr(stats, "load_recruitment", lambda recruitment_id: recruitments[recruitment_id])

    result = stats.get_workspace_statistics()

    assert result["total_recruitments"] == 2
    assert result["complete_recruitments"] == 1
    assert result["draft_recruitments"] == 1
    assert result["total_candidates"] == 2
    assert result["average_match"] == 85
    assert result["average_confidence"] == 90
    assert result["candidates_above_90"] == 1
    assert result["candidates_above_85"] == 1
    assert result["top_candidate"]["name"] == "Emma Martin"
    assert result["top_candidate"]["score"] == 92


def test_get_ai_insights_with_no_recruitments(monkeypatch):
    monkeypatch.setattr(
        stats,
        "get_workspace_statistics",
        lambda: {
            "total_recruitments": 0,
            "complete_recruitments": 0,
            "draft_recruitments": 0,
            "total_candidates": 0,
            "average_match": 0,
            "average_confidence": 0,
            "candidates_above_90": 0,
            "candidates_above_85": 0,
            "top_candidate": None,
            "recent_recruitments": [],
        },
    )

    insights = stats.get_ai_insights()

    assert len(insights) == 2
    assert "Create your first recruitment" in insights[0]


def test_get_ai_insights_with_existing_data(monkeypatch):
    monkeypatch.setattr(
        stats,
        "get_workspace_statistics",
        lambda: {
            "total_recruitments": 3,
            "complete_recruitments": 2,
            "draft_recruitments": 1,
            "total_candidates": 12,
            "average_match": 84,
            "average_confidence": 91,
            "candidates_above_90": 4,
            "candidates_above_85": 7,
            "top_candidate": {"name": "Emma Martin", "score": 96},
            "recent_recruitments": [],
        },
    )

    insights = stats.get_ai_insights()

    assert "3 recruitment project(s) saved in your workspace." in insights
    assert "2 recruitment(s) already include AI candidate analysis." in insights
    assert "1 recruitment(s) still need candidate analysis." in insights
    assert "12 candidate(s) analyzed across all recruitments." in insights
    assert "4 candidate(s) scored 90% or higher." in insights
    assert "Average match score across analyzed candidates is 84%." in insights
    assert "Average AI confidence is 91%." in insights
