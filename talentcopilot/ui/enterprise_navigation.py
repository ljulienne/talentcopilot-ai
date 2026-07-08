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
            "Daily cockpit and product overview.",
            [
                EnterprisePage("Recruitment Command Center", "talentcopilot.ui.command_center", "render_command_center", "⌂", "What needs attention today."),
                EnterprisePage("Product Overview", "talentcopilot.ui.product_overview", "render_product_overview", "◇", "Understand the product and demo flow."),
            ],
        ),
        "recruitment": EnterpriseSection(
            "Recruitment",
            "Create, open and pilot recruitment workflows.",
            [
                EnterprisePage("New Recruitment", "talentcopilot.ui.recruitment_wizard", "render_new_recruitment", "＋", "Create a recruitment."),
                EnterprisePage("Open Recruitment", "talentcopilot.ui.open_recruitment", "render_open_recruitment", "▣", "Resume recruitment."),
                EnterprisePage("Recruitment Workspace", "talentcopilot.ui.recruitment_workspace", "render_recruitment_workspace", "▦", "Pilot the active recruitment."),
            ],
        ),
        "analysis": EnterpriseSection(
            "Analysis",
            "Review candidates, compare profiles and understand talent coverage.",
            [
                EnterprisePage("Candidate Workspace", "talentcopilot.ui.candidate_workspace", "render_candidate_workspace", "◉", "Review candidates one by one."),
                EnterprisePage("Talent Intelligence", "talentcopilot.ui.talent_intelligence", "render_talent_intelligence", "⌕", "Understand talent coverage and sourcing readiness."),
                EnterprisePage("Comparison", "talentcopilot.ui.comparison_workspace", "render_comparison_workspace", "⇄", "Compare candidates through decision signals."),
            ],
        ),
        "interview": EnterpriseSection(
            "Interview",
            "Prepare structured interviews and score candidate evidence.",
            [
                EnterprisePage("Interview Workspace", "talentcopilot.ui.interview_workspace", "render_interview_workspace", "▥", "Prepare interviews with AI questions and scorecards."),
            ],
        ),
        "decision": EnterpriseSection(
            "Decision",
            "Move from analysis to action and collaborative decision.",
            [
                EnterprisePage("Decision Board", "talentcopilot.ui.decision_board", "render_decision_board", "◆", "Make collaborative decisions."),
                EnterprisePage("Recruiter Copilot", "talentcopilot.ui.recruiter_copilot_workspace", "render_recruiter_copilot_workspace", "✦", "Act on AI guidance."),
                EnterprisePage("Hiring Budget", "talentcopilot.ui.hiring_budget", "render_hiring_budget", "¤", "Assess financial feasibility without changing fit score."),
            ],
        ),
        "reporting": EnterpriseSection(
            "Reporting",
            "Prepare stakeholder-ready outputs and analytics.",
            [
                EnterprisePage("Executive Reporting", "talentcopilot.ui.executive_reporting", "render_executive_reporting", "▤", "Prepare stakeholder-ready reports."),
                EnterprisePage("Analytics Dashboard", "talentcopilot.ui.analytics_dashboard", "render_analytics_dashboard", "▧", "Track recruitment health and KPIs."),
            ],
        ),
        "administration": EnterpriseSection(
            "Administration",
            "Demo, health, settings and design system.",
            [
                EnterprisePage("Enterprise Demo Final", "talentcopilot.ui.enterprise_demo_final", "render_enterprise_demo_final", "▶", "Run the final Release 1.1 demo."),
                EnterprisePage("Demo Experience", "talentcopilot.ui.demo_experience", "render_demo_experience", "▶", "Prepare a reliable demo."),
                EnterprisePage("Release Summary", "talentcopilot.ui.release_summary", "render_release_summary", "★", "Review Release 1.0 status."),
                EnterprisePage("Release Readiness", "talentcopilot.ui.release_readiness", "render_release_readiness", "✓", "Validate release health."),
                EnterprisePage("Session Health", "talentcopilot.ui.session_health", "render_session_health", "◌", "Check session quality."),
                EnterprisePage("UI Showcase", "talentcopilot.ui.ui_showcase", "render_ui_showcase", "◧", "View TalentCopilot Design System components."),
                EnterprisePage("Settings", "talentcopilot.ui.settings", "render_settings", "⚙", "Configure the app."),
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
