from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EnterprisePage:
    label: str
    module: str
    function: str
    icon: str


@dataclass(frozen=True)
class EnterpriseSection:
    label: str
    pages: List[EnterprisePage]


def get_enterprise_navigation() -> Dict[str, EnterpriseSection]:
    return {
        "Command": EnterpriseSection(
            "Command",
            [EnterprisePage("Recruitment Command Center", "talentcopilot.ui.command_center", "render_command_center", "⌂")],
        ),
        "Recruitment": EnterpriseSection(
            "Recruitment",
            [
                EnterprisePage("New Recruitment", "talentcopilot.ui.recruitment_wizard", "render_new_recruitment", "＋"),
                EnterprisePage("Open Recruitment", "talentcopilot.ui.open_recruitment", "render_open_recruitment", "▣"),
            ],
        ),
        "Analysis": EnterpriseSection(
            "Analysis",
            [
                EnterprisePage("Candidate Workspace", "talentcopilot.ui.candidates_v2", "render_candidates_v2", "◉"),
                EnterprisePage("Talent Intelligence", "talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2", "⌕"),
                EnterprisePage("Comparison", "talentcopilot.ui.comparison_v2", "render_comparison_v2", "⇄"),
            ],
        ),
        "Decision": EnterpriseSection(
            "Decision",
            [
                EnterprisePage("Decision Center", "talentcopilot.ui.dashboard_v2", "render_dashboard_v2", "◆"),
                EnterprisePage("Recruiter Copilot", "talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2", "✦"),
                EnterprisePage("Decision Workspace", "talentcopilot.ui.decision_workspace", "render_decision_workspace", "◇"),
            ],
        ),
        "Reporting": EnterpriseSection(
            "Reporting",
            [EnterprisePage("Executive Reporting", "talentcopilot.ui.reports_v2", "render_reports_v2", "▤")],
        ),
        "Administration": EnterpriseSection(
            "Administration",
            [
                EnterprisePage("Session Health", "talentcopilot.ui.session_health", "render_session_health", "◌"),
                EnterprisePage("Settings", "talentcopilot.ui.settings", "render_settings", "⚙"),
            ],
        ),
    }


def flatten_enterprise_pages():
    pages = []
    for section in get_enterprise_navigation().values():
        pages.extend(section.pages)
    return pages
