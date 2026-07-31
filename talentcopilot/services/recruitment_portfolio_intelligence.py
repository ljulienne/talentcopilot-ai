"""Operational intelligence across persisted recruitment projects.

Release 8.6.0 adds transparent, domain-agnostic portfolio signals based on
project lifecycle, priority, owner and last activity. The service deliberately
avoids predictive time-to-hire claims and never reads or mutates candidate
score fields.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Iterable, Sequence

from talentcopilot.models.recruitment_portfolio_intelligence import (
    PortfolioAlert,
    PortfolioFreshnessMetric,
    PortfolioLifecycleMetric,
    PortfolioOwnerLoad,
    RecruitmentPortfolioIntelligenceReport,
)
from talentcopilot.services.recruitment_project_portfolio import (
    LIFECYCLE_ANALYZING,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_DECIDED,
    LIFECYCLE_DECISION_READY,
    LIFECYCLE_DRAFT,
    LIFECYCLE_INTERVIEW,
    LIFECYCLE_LABELS,
    LIFECYCLE_REVIEW,
    ProjectPortfolioSummary,
)


SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Info": 3}
PRIORITY_ORDER = {"Critical": 0, "High": 1, "Normal": 2}

FRESHNESS_RECENT = "recent"
FRESHNESS_WATCH = "watch"
FRESHNESS_STALE = "stale"
FRESHNESS_UNKNOWN = "unknown"

FRESHNESS_LABELS = {
    FRESHNESS_RECENT: "Updated within 3 days",
    FRESHNESS_WATCH: "Updated 4–7 days ago",
    FRESHNESS_STALE: "No activity for more than 7 days",
    FRESHNESS_UNKNOWN: "Last activity unavailable",
}


class RecruitmentPortfolioIntelligenceService:
    """Build transparent operational signals for a recruitment portfolio."""

    def build(
        self,
        projects: Iterable[ProjectPortfolioSummary],
        *,
        now: datetime | None = None,
    ) -> RecruitmentPortfolioIntelligenceReport:
        generated_at = self._normalise_now(now)
        open_projects = tuple(project for project in projects if project.lifecycle != LIFECYCLE_ARCHIVED)

        ages = {
            project.project_id: self.activity_age_days(project.updated_at, now=generated_at)
            for project in open_projects
        }
        alerts = tuple(
            sorted(
                (
                    alert
                    for project in open_projects
                    if (alert := self._primary_alert(project, ages[project.project_id])) is not None
                ),
                key=lambda item: (
                    SEVERITY_ORDER.get(item.severity, 9),
                    PRIORITY_ORDER.get(item.priority, 9),
                    -(item.activity_age_days or 0),
                    item.project_title.casefold(),
                ),
            )
        )
        alerted_ids = {alert.project_id for alert in alerts}

        lifecycle_metrics = self._lifecycle_metrics(open_projects)
        owner_load = self._owner_load(open_projects, alerts)
        freshness_metrics = self._freshness_metrics(open_projects, ages)

        stale_count = sum(
            age is not None and age > 7
            for age in ages.values()
        )
        unassigned_count = sum(self._is_unassigned(project.owner) for project in open_projects)
        critical_count = sum(project.priority == "Critical" for project in open_projects)
        decision_ready_count = sum(
            project.lifecycle == LIFECYCLE_DECISION_READY
            for project in open_projects
        )
        decided_count = sum(project.lifecycle == LIFECYCLE_DECIDED for project in open_projects)

        return RecruitmentPortfolioIntelligenceReport(
            generated_at=generated_at.replace(microsecond=0).isoformat(),
            active_project_count=len(open_projects),
            candidate_count=sum(project.candidate_count for project in open_projects),
            decision_ready_count=decision_ready_count,
            decided_count=decided_count,
            attention_project_count=len(alerted_ids),
            stale_project_count=stale_count,
            unassigned_project_count=unassigned_count,
            critical_project_count=critical_count,
            lifecycle_metrics=lifecycle_metrics,
            owner_load=owner_load,
            freshness_metrics=freshness_metrics,
            alerts=alerts,
            recommendations=self._recommendations(alerts, open_projects),
        )

    @staticmethod
    def _normalise_now(now: datetime | None) -> datetime:
        value = now or datetime.now(timezone.utc)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @classmethod
    def activity_age_days(cls, updated_at: str, *, now: datetime | None = None) -> int | None:
        text = str(updated_at or "").strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        reference = cls._normalise_now(now)
        elapsed = reference - parsed.astimezone(timezone.utc)
        return max(0, int(elapsed.total_seconds() // 86400))

    @staticmethod
    def _is_unassigned(owner: str) -> bool:
        return str(owner or "").strip().casefold() in {"", "unassigned", "not assigned", "none"}

    def _primary_alert(
        self,
        project: ProjectPortfolioSummary,
        age_days: int | None,
    ) -> PortfolioAlert | None:
        unassigned = self._is_unassigned(project.owner)
        priority = project.priority if project.priority in PRIORITY_ORDER else "Normal"

        if priority == "Critical" and unassigned:
            return self._alert(
                project,
                age_days,
                severity="Critical",
                category="Ownership",
                summary="A critical recruitment has no accountable owner.",
                action="Assign an owner before the next project update.",
            )

        if priority == "Critical" and age_days is not None and age_days > 7:
            return self._alert(
                project,
                age_days,
                severity="Critical",
                category="Activity",
                summary=f"This critical recruitment has had no recorded activity for {age_days} days.",
                action=project.next_action,
            )

        if project.lifecycle == LIFECYCLE_DECISION_READY and age_days is not None and age_days > 3:
            return self._alert(
                project,
                age_days,
                severity="High",
                category="Decision",
                summary=f"Finalists are ready, but no final decision has been recorded for {age_days} days.",
                action="Review finalists and record the human-owned decision.",
            )

        if project.lifecycle == LIFECYCLE_INTERVIEW and age_days is not None and age_days > 5:
            return self._alert(
                project,
                age_days,
                severity="High",
                category="Interview",
                summary=f"Interview work has not been updated for {age_days} days.",
                action="Continue or close the structured interview cycle.",
            )

        if project.lifecycle in {LIFECYCLE_ANALYZING, LIFECYCLE_REVIEW} and age_days is not None and age_days > 7:
            return self._alert(
                project,
                age_days,
                severity="High" if priority in {"Critical", "High"} else "Medium",
                category="Workflow",
                summary=f"The recruitment has remained in {project.status.lower()} without activity for {age_days} days.",
                action=project.next_action,
            )

        if priority in {"Critical", "High"} and project.lifecycle == LIFECYCLE_DRAFT and project.candidate_count == 0:
            return self._alert(
                project,
                age_days,
                severity="High",
                category="Pipeline",
                summary="A priority recruitment has no candidate pipeline yet.",
                action="Add candidates or review the sourcing plan.",
            )

        if unassigned:
            return self._alert(
                project,
                age_days,
                severity="Medium",
                category="Ownership",
                summary="No project owner is recorded.",
                action="Assign an owner to clarify accountability.",
            )

        if age_days is None:
            return self._alert(
                project,
                age_days,
                severity="Medium",
                category="Data quality",
                summary="The last project activity timestamp is unavailable.",
                action="Open and save the project to refresh its activity metadata.",
            )

        return None

    @staticmethod
    def _alert(
        project: ProjectPortfolioSummary,
        age_days: int | None,
        *,
        severity: str,
        category: str,
        summary: str,
        action: str,
    ) -> PortfolioAlert:
        return PortfolioAlert(
            project_id=project.project_id,
            project_title=project.title,
            severity=severity,
            category=category,
            summary=summary,
            recommended_action=action,
            lifecycle=project.lifecycle,
            owner=project.owner,
            priority=project.priority,
            activity_age_days=age_days,
        )

    @staticmethod
    def _lifecycle_metrics(
        projects: Sequence[ProjectPortfolioSummary],
    ) -> tuple[PortfolioLifecycleMetric, ...]:
        order = (
            LIFECYCLE_DRAFT,
            LIFECYCLE_ANALYZING,
            LIFECYCLE_REVIEW,
            LIFECYCLE_INTERVIEW,
            LIFECYCLE_DECISION_READY,
            LIFECYCLE_DECIDED,
        )
        metrics = []
        for lifecycle in order:
            selected = tuple(project for project in projects if project.lifecycle == lifecycle)
            metrics.append(
                PortfolioLifecycleMetric(
                    lifecycle=lifecycle,
                    label=LIFECYCLE_LABELS[lifecycle],
                    project_count=len(selected),
                    candidate_count=sum(project.candidate_count for project in selected),
                )
            )
        return tuple(metrics)

    @staticmethod
    def _owner_load(
        projects: Sequence[ProjectPortfolioSummary],
        alerts: Sequence[PortfolioAlert],
    ) -> tuple[PortfolioOwnerLoad, ...]:
        by_owner: dict[str, list[ProjectPortfolioSummary]] = defaultdict(list)
        alert_counts = Counter(alert.owner for alert in alerts)
        for project in projects:
            by_owner[project.owner or "Unassigned"].append(project)

        rows = []
        for owner, owned in by_owner.items():
            rows.append(
                PortfolioOwnerLoad(
                    owner=owner,
                    project_count=len(owned),
                    critical_or_high_count=sum(
                        project.priority in {"Critical", "High"}
                        for project in owned
                    ),
                    decision_ready_count=sum(
                        project.lifecycle == LIFECYCLE_DECISION_READY
                        for project in owned
                    ),
                    attention_count=alert_counts.get(owner, 0),
                )
            )
        return tuple(
            sorted(
                rows,
                key=lambda row: (
                    -row.attention_count,
                    -row.critical_or_high_count,
                    -row.project_count,
                    row.owner.casefold(),
                ),
            )
        )

    @staticmethod
    def _freshness_band(age_days: int | None) -> str:
        if age_days is None:
            return FRESHNESS_UNKNOWN
        if age_days <= 3:
            return FRESHNESS_RECENT
        if age_days <= 7:
            return FRESHNESS_WATCH
        return FRESHNESS_STALE

    def _freshness_metrics(
        self,
        projects: Sequence[ProjectPortfolioSummary],
        ages: dict[str, int | None],
    ) -> tuple[PortfolioFreshnessMetric, ...]:
        counts = Counter(
            self._freshness_band(ages[project.project_id])
            for project in projects
        )
        order = (
            FRESHNESS_RECENT,
            FRESHNESS_WATCH,
            FRESHNESS_STALE,
            FRESHNESS_UNKNOWN,
        )
        return tuple(
            PortfolioFreshnessMetric(
                band=band,
                label=FRESHNESS_LABELS[band],
                project_count=counts.get(band, 0),
            )
            for band in order
        )

    @staticmethod
    def _recommendations(
        alerts: Sequence[PortfolioAlert],
        projects: Sequence[ProjectPortfolioSummary],
    ) -> tuple[str, ...]:
        recommendations: list[str] = []
        if any(alert.category == "Ownership" for alert in alerts):
            recommendations.append("Assign owners to unassigned projects before changing priorities or deadlines.")
        if any(alert.category == "Decision" for alert in alerts):
            recommendations.append("Resolve decision-ready projects first to reduce avoidable finalist waiting time.")
        if any(alert.category in {"Activity", "Workflow", "Interview"} for alert in alerts):
            recommendations.append("Review projects with stale activity and either advance, pause or archive them explicitly.")
        if any(project.priority == "Critical" for project in projects):
            recommendations.append("Keep critical projects visible in the attention queue until their next action is completed.")
        if not recommendations and projects:
            recommendations.append("No operational alert is currently detected; continue recording project activity consistently.")
        if not projects:
            recommendations.append("Save at least one recruitment project to enable cross-project intelligence.")
        return tuple(recommendations)
