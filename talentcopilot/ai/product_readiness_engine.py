from typing import Any, List

from talentcopilot.models.product_readiness import (
    ProductReadinessReport,
    ReadinessCheck,
    ReadinessLevel,
    ReadinessSeverity,
)
from talentcopilot.services.versioning import get_app_name, get_app_version


class ProductReadinessEngine:
    """
    Evaluates whether TalentCopilot is ready for a product demo.
    """

    def assess(self, session: Any = None, workflow_report: Any = None) -> ProductReadinessReport:
        checks: List[ReadinessCheck] = []
        checks.extend(self._session_checks(session))
        checks.extend(self._workflow_checks(workflow_report))
        checks.extend(self._import_checks())

        score = self._score(checks)
        level = self._level(score, checks)
        summary = (
            f"{get_app_name()} {get_app_version()} readiness is {level.value} "
            f"with score {score}/100."
        )

        return ProductReadinessReport(
            product_name=get_app_name(),
            version=get_app_version(),
            readiness_score=score,
            readiness_level=level,
            checks=checks,
            summary=summary,
        )

    def _session_checks(self, session: Any) -> List[ReadinessCheck]:
        if session is None:
            return [
                ReadinessCheck(
                    name="Recruitment session",
                    passed=False,
                    severity=ReadinessSeverity.WARNING,
                    message="No active recruitment session available.",
                    recommendation="Create or run a RecruitmentSession before demo.",
                )
            ]

        candidate_count = getattr(session, "candidate_count", 0)
        analyzed_count = getattr(session, "analyzed_count", 0)
        error_count = getattr(session, "error_count", 0)

        return [
            ReadinessCheck(
                name="Recruitment session",
                passed=True,
                severity=ReadinessSeverity.INFO,
                message="Recruitment session is available.",
            ),
            ReadinessCheck(
                name="Candidate coverage",
                passed=candidate_count > 0,
                severity=ReadinessSeverity.WARNING,
                message=f"{candidate_count} candidate(s) available.",
                recommendation="Add demo candidates." if candidate_count == 0 else "",
            ),
            ReadinessCheck(
                name="Analysis coverage",
                passed=analyzed_count > 0,
                severity=ReadinessSeverity.WARNING,
                message=f"{analyzed_count} candidate analysis result(s) available.",
                recommendation="Run EnterprisePipeline." if analyzed_count == 0 else "",
            ),
            ReadinessCheck(
                name="Pipeline errors",
                passed=error_count == 0,
                severity=ReadinessSeverity.CRITICAL,
                message=f"{error_count} pipeline error(s) detected.",
                recommendation="Review candidate analysis errors." if error_count else "",
            ),
        ]

    def _workflow_checks(self, workflow_report: Any) -> List[ReadinessCheck]:
        if workflow_report is None:
            return [
                ReadinessCheck(
                    name="Recruiter workflow",
                    passed=False,
                    severity=ReadinessSeverity.WARNING,
                    message="No recruiter workflow report available.",
                    recommendation="Build workflow from RecruitmentSession.",
                )
            ]

        blocked_count = getattr(workflow_report, "blocked_count", 0)
        next_action = getattr(workflow_report, "recommended_next_action", "")

        return [
            ReadinessCheck(
                name="Recruiter workflow",
                passed=True,
                severity=ReadinessSeverity.INFO,
                message="Recruiter workflow report is available.",
            ),
            ReadinessCheck(
                name="Workflow blockers",
                passed=blocked_count == 0,
                severity=ReadinessSeverity.CRITICAL,
                message=f"{blocked_count} workflow blocker(s) detected.",
                recommendation="Resolve workflow blockers." if blocked_count else "",
            ),
            ReadinessCheck(
                name="Next action",
                passed=bool(next_action),
                severity=ReadinessSeverity.INFO,
                message=next_action or "No next action available.",
            ),
        ]

    def _import_checks(self) -> List[ReadinessCheck]:
        modules = [
            "talentcopilot.ai.enterprise_pipeline",
            "talentcopilot.ai.recruiter_workflow_engine",
            "talentcopilot.ui.enterprise_components",
            "talentcopilot.ui.product_readiness_cards",
        ]

        checks = []
        for module_name in modules:
            try:
                __import__(module_name)
                checks.append(ReadinessCheck(
                    name=f"Import {module_name}",
                    passed=True,
                    severity=ReadinessSeverity.INFO,
                    message="Import OK.",
                ))
            except Exception as exc:
                checks.append(ReadinessCheck(
                    name=f"Import {module_name}",
                    passed=False,
                    severity=ReadinessSeverity.CRITICAL,
                    message=str(exc),
                    recommendation="Fix missing or broken module.",
                ))
        return checks

    def _score(self, checks: List[ReadinessCheck]) -> float:
        if not checks:
            return 0.0
        weights = {
            ReadinessSeverity.INFO: 1.0,
            ReadinessSeverity.WARNING: 1.5,
            ReadinessSeverity.CRITICAL: 2.5,
        }
        total = sum(weights[check.severity] for check in checks)
        passed = sum(weights[check.severity] for check in checks if check.passed)
        return round((passed / total) * 100, 2)

    def _level(self, score: float, checks: List[ReadinessCheck]) -> ReadinessLevel:
        critical_failures = [
            check for check in checks
            if not check.passed and check.severity == ReadinessSeverity.CRITICAL
        ]
        if critical_failures:
            return ReadinessLevel.NOT_READY
        if score >= 90:
            return ReadinessLevel.EXCELLENT
        if score >= 75:
            return ReadinessLevel.GOOD
        if score >= 50:
            return ReadinessLevel.PARTIAL
        return ReadinessLevel.NOT_READY
