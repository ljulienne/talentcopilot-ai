from talentcopilot.models.release_readiness import ReadinessCheck, ReleaseReadinessReport


class ReleaseReadinessService:
    def build(self) -> ReleaseReadinessReport:
        checks = [
            self._check_import("Enterprise navigation", "talentcopilot.ui.enterprise_navigation", "get_enterprise_navigation"),
            self._check_import("Design system theme", "talentcopilot.ui.design_system.theme", "apply_enterprise_theme"),
            self._check_import("Command Center", "talentcopilot.ui.command_center", "render_command_center"),
            self._check_import("Session bridge", "talentcopilot.services.streamlit_session_bridge", "get_streamlit_session"),
            self._check_navigation_targets(),
        ]

        passed = len([check for check in checks if check.status == "OK"])
        score = int((passed / max(1, len(checks))) * 100)

        recommendations = []
        if score < 100:
            recommendations.append("Review failed checks before demo or Streamlit reboot.")
        else:
            recommendations.append("Application shell is ready for demo validation.")

        recommendations.append("Run python -m pytest before pushing a release.")
        recommendations.append("Reboot Streamlit Cloud after GitHub push.")

        return ReleaseReadinessReport(
            score=score,
            status="Ready" if score == 100 else "Needs attention",
            checks=checks,
            recommendations=recommendations,
        )

    def _check_import(self, name: str, module_name: str, attr: str) -> ReadinessCheck:
        try:
            module = __import__(module_name, fromlist=[attr])
            if hasattr(module, attr):
                return ReadinessCheck(name, "OK", f"{module_name}.{attr}")
            return ReadinessCheck(name, "FAIL", f"Missing attribute: {attr}")
        except Exception as exc:
            return ReadinessCheck(name, "FAIL", str(exc))

    def _check_navigation_targets(self) -> ReadinessCheck:
        try:
            from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages

            missing = []
            for page in flatten_enterprise_pages():
                try:
                    module = __import__(page.module, fromlist=[page.function])
                    if not hasattr(module, page.function):
                        missing.append(page.label)
                except Exception:
                    missing.append(page.label)

            if missing:
                return ReadinessCheck("Navigation targets", "FAIL", ", ".join(missing[:8]))

            return ReadinessCheck("Navigation targets", "OK", "All navigation targets import correctly.")
        except Exception as exc:
            return ReadinessCheck("Navigation targets", "FAIL", str(exc))
