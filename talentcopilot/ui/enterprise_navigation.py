from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EnterprisePage:
    label: str
    module: str
    function: str
    icon: str
    description: str = ""


@dataclass(frozen=True)
class EnterpriseSection:
    label: str
    description: str
    pages: List[EnterprisePage]


def get_enterprise_navigation() -> Dict[str, EnterpriseSection]:
    return {
        "command": EnterpriseSection(
            "Command",
            "Daily cockpit and priorities.",
            [EnterprisePage("Recruitment Command Center", "talentcopilot.ui.command_center", "render_command_center", "⌂", "What needs attention today.")],
        ),
        "recruitment": EnterpriseSection(
            "Recruitment",
            "Create and resume recruitment workflows.",
            [
                EnterprisePage("New Recruitment", "talentcopilot.ui.recruitment_wizard", "render_new_recruitment", "＋", "Create a recruitment."),
                EnterprisePage("Open Recruitment", "talentcopilot.ui.open_recruitment", "render_open_recruitment", "▣", "Resume recruitment."),
            ],
        ),
        "analysis": EnterpriseSection(
            "Analysis",
            "Review candidates and talent signals.",
            [
                EnterprisePage("Candidate Workspace", "talentcopilot.ui.candidates_v2", "render_candidates_v2", "◉", "Review candidates."),
                EnterprisePage("Talent Intelligence", "talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2", "⌕", "Find and understand talent."),
                EnterprisePage("Comparison", "talentcopilot.ui.comparison_v2", "render_comparison_v2", "⇄", "Compare candidates."),
            ],
        ),
        "decision": EnterpriseSection(
            "Decision",
            "Use AI guidance and human review.",
            [
                EnterprisePage("Decision Center", "talentcopilot.ui.dashboard_v2", "render_dashboard_v2", "◆", "Control the decision process."),
                EnterprisePage("Recruiter Copilot", "talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2", "✦", "Act on AI guidance."),
                EnterprisePage("Decision Workspace", "talentcopilot.ui.decision_workspace", "render_decision_workspace", "◇", "Review governance and explainability."),
            ],
        ),
        "reporting": EnterpriseSection(
            "Reporting",
            "Prepare stakeholder-ready outputs.",
            [EnterprisePage("Executive Reporting", "talentcopilot.ui.reports_v2", "render_reports_v2", "▤", "Prepare outputs.")],
        ),
        "administration": EnterpriseSection(
            "Administration",
            "Health, settings and design system.",
            [
                EnterprisePage("Session Health", "talentcopilot.ui.session_health", "render_session_health", "◌", "Check session quality."),
                EnterprisePage("Settings", "talentcopilot.ui.settings", "render_settings", "⚙", "Configure the app."),
                EnterprisePage("UI Showcase", "talentcopilot.ui.ui_showcase", "render_ui_showcase", "◧", "View TalentCopilot Design System components."),
            ],
        ),
    }


def flatten_enterprise_pages():
    pages = []
    for section in get_enterprise_navigation().values():
        pages.extend(section.pages)
    return pages


def get_page_by_label(label: str):
    for page in flatten_enterprise_pages():
        if page.label == label:
            return page
    return None
