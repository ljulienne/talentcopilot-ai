import importlib
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


@dataclass
class ImportAuditResult:
    checked: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def as_dict(self) -> Dict:
        return {
            "ok": self.ok,
            "checked": self.checked,
            "missing": self.missing,
        }


class ImportSafetyAudit:
    """
    Validates critical imports before Streamlit Cloud deployment.
    """

    CRITICAL_IMPORTS: List[Tuple[str, str]] = [
        ("talentcopilot.ui.theme", "apply_theme"),
        ("talentcopilot.ui.premium_theme", "apply_premium_ui"),
        ("talentcopilot.ui.sidebar", "render_sidebar_brand"),
        ("talentcopilot.ui.home_v2", "render_home_v2"),
        ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        ("talentcopilot.ui.decision_workspace", "render_decision_workspace"),
        ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        ("talentcopilot.ui.reports_v2", "render_reports_v2"),
        ("talentcopilot.ui.decision_cards", "render_decision_intelligence_card"),
        ("talentcopilot.ui.governance_cards", "render_governance_card"),
        ("talentcopilot.ai.enterprise_pipeline", "EnterprisePipeline"),
        ("talentcopilot.services.demo_session_factory", "DemoSessionFactory"),
    ]

    def audit(self, imports: Iterable[Tuple[str, str]] = None) -> Dict:
        result = ImportAuditResult()
        for module_name, attr in list(imports or self.CRITICAL_IMPORTS):
            label = f"{module_name}.{attr}"
            result.checked.append(label)
            try:
                module = importlib.import_module(module_name)
                getattr(module, attr)
            except Exception as exc:
                result.missing.append(f"{label}: {exc}")
        return result.as_dict()

    def audit_navigation(self, navigation: Dict[str, Tuple[str, str]]) -> Dict:
        return self.audit(navigation.values())
