from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from talentcopilot.services.recruitment_portfolio_intelligence import (
    RecruitmentPortfolioIntelligenceService,
)
from talentcopilot.services.recruitment_project_portfolio import (
    LIFECYCLE_ANALYZING,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_DECIDED,
    LIFECYCLE_DECISION_READY,
    LIFECYCLE_DRAFT,
    LIFECYCLE_INTERVIEW,
    LIFECYCLE_REVIEW,
    ProjectPortfolioSummary,
)


NOW = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)


def _project(
    project_id: str,
    title: str,
    *,
    lifecycle: str = LIFECYCLE_REVIEW,
    priority: str = "Normal",
    owner: str = "Recruiter A",
    updated_at: str = "2026-07-30T08:00:00+00:00",
    candidate_count: int = 3,
    analyzed_count: int = 3,
) -> ProjectPortfolioSummary:
    return ProjectPortfolioSummary(
        project_id=project_id,
        title=title,
        role_title=title,
        project_type="Recruitment",
        lifecycle=lifecycle,
        priority=priority,
        owner=owner,
        location="Remote",
        candidate_count=candidate_count,
        analyzed_count=analyzed_count,
        interview_count=1 if lifecycle == LIFECYCLE_INTERVIEW else 0,
        finalist_count=2 if lifecycle == LIFECYCLE_DECISION_READY else 0,
        decision_recorded=lifecycle == LIFECYCLE_DECIDED,
        updated_at=updated_at,
        source="storage",
    )


def test_portfolio_intelligence_is_domain_agnostic_and_excludes_archives():
    projects = (
        _project("sales", "Senior Sales Manager", lifecycle=LIFECYCLE_DECISION_READY),
        _project("engineering", "Platform Engineer", lifecycle=LIFECYCLE_ANALYZING),
        _project("finance", "Finance Director", lifecycle=LIFECYCLE_DECIDED),
        _project("nurse", "Clinical Nurse Manager", lifecycle=LIFECYCLE_ARCHIVED),
    )

    report = RecruitmentPortfolioIntelligenceService().build(projects, now=NOW)

    assert report.active_project_count == 3
    assert report.candidate_count == 9
    assert report.decision_ready_count == 1
    assert report.decided_count == 1
    assert all(item.lifecycle != LIFECYCLE_ARCHIVED for item in report.lifecycle_metrics)
    assert {item.label for item in report.lifecycle_metrics} >= {
        "Analyzing",
        "Decision ready",
        "Decided",
    }


def test_one_primary_alert_per_project_with_transparent_priority():
    projects = (
        _project(
            "critical-unowned",
            "Global Operations Director",
            lifecycle=LIFECYCLE_REVIEW,
            priority="Critical",
            owner="Unassigned",
            updated_at="2026-07-10T12:00:00+00:00",
        ),
        _project(
            "decision-stale",
            "Marketing Director",
            lifecycle=LIFECYCLE_DECISION_READY,
            updated_at="2026-07-24T12:00:00+00:00",
        ),
        _project(
            "interview-stale",
            "Data Analyst",
            lifecycle=LIFECYCLE_INTERVIEW,
            updated_at="2026-07-20T12:00:00+00:00",
        ),
    )

    report = RecruitmentPortfolioIntelligenceService().build(projects, now=NOW)

    assert len(report.alerts) == 3
    assert len({alert.project_id for alert in report.alerts}) == 3
    assert report.alerts[0].project_id == "critical-unowned"
    assert report.alerts[0].severity == "Critical"
    assert report.alerts[0].category == "Ownership"
    assert "score" not in " ".join(alert.summary.casefold() for alert in report.alerts)


def test_activity_age_and_freshness_are_based_on_recorded_timestamps():
    service = RecruitmentPortfolioIntelligenceService()

    assert service.activity_age_days("2026-07-30T11:00:00+00:00", now=NOW) == 0
    assert service.activity_age_days("2026-07-25T12:00:00+00:00", now=NOW) == 5
    assert service.activity_age_days("2026-07-20T12:00:00+00:00", now=NOW) == 10
    assert service.activity_age_days("", now=NOW) is None

    report = service.build(
        (
            _project("recent", "Product Manager", updated_at="2026-07-29T12:00:00+00:00"),
            _project("watch", "Legal Counsel", updated_at="2026-07-25T12:00:00+00:00"),
            _project("stale", "Plant Manager", updated_at="2026-07-20T12:00:00+00:00"),
            _project("unknown", "Buyer", updated_at=""),
        ),
        now=NOW,
    )
    freshness = {item.band: item.project_count for item in report.freshness_metrics}
    assert freshness == {"recent": 1, "watch": 1, "stale": 1, "unknown": 1}
    assert report.stale_project_count == 1


def test_owner_workload_is_descriptive_and_attention_aware():
    report = RecruitmentPortfolioIntelligenceService().build(
        (
            _project(
                "a",
                "HRIS Manager",
                owner="Recruiter A",
                priority="Critical",
                updated_at="2026-07-10T12:00:00+00:00",
            ),
            _project(
                "b",
                "Supply Chain Director",
                owner="Recruiter A",
                lifecycle=LIFECYCLE_DECISION_READY,
            ),
            _project(
                "c",
                "Software Engineer",
                owner="Recruiter B",
                lifecycle=LIFECYCLE_DRAFT,
                candidate_count=0,
                analyzed_count=0,
            ),
        ),
        now=NOW,
    )

    owner_a = next(item for item in report.owner_load if item.owner == "Recruiter A")
    assert owner_a.project_count == 2
    assert owner_a.critical_or_high_count == 1
    assert owner_a.decision_ready_count == 1
    assert owner_a.attention_count == 1


def test_analytics_ui_exposes_portfolio_intelligence_without_predictive_claims():
    source = Path("talentcopilot/ui/analytics_dashboard.py").read_text(encoding="utf-8")
    assert "Recruitment Portfolio Intelligence" in source
    assert "Attention queue" in source
    assert "Owner workload" in source
    assert "One primary operational alert is shown per project" in source
    assert "time-to-hire" not in source.casefold()
    assert "match_score" not in source
    assert "decision_score" not in source


def test_service_never_reads_candidate_score_or_rank_fields():
    source = Path("talentcopilot/services/recruitment_portfolio_intelligence.py").read_text(
        encoding="utf-8"
    )
    forbidden = ("match_score", "decision_score", "mission_rank", "decision_rank")
    assert not any(item in source for item in forbidden)


def test_visible_version_is_release_8_6_0_or_later():
    from talentcopilot.config import APP_VERSION

    version = tuple(int(part) for part in APP_VERSION.lstrip("v").split("."))
    assert version >= (8, 6, 0)
