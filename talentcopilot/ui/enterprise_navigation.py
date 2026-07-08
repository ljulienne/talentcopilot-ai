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
            "Start here: product story and daily cockpit.",
            [
                EnterprisePage("Product Overview", "talentcopilot.ui.product_overview", "render_product_overview", "◇", "Understand the product and demo flow."),
                EnterprisePage("Recruitment Command Center", "talentcopilot.ui.command_center", "render_command_center", "⌂", "What needs attention today."),
            ],
        ),
        "recruitment": EnterpriseSection(
            "Recruitment",
            "Create, open and operate recruitment workflows.",
            [
                EnterprisePage("New Recruitment", "talentcopilot.ui.recruitment_wizard", "render_new_recruitment", "＋", "Create a recruitment."),
                EnterprisePage("Open Recruitment", "talentcopilot.ui.open_recruitment", "render_open_recruitment", "▣", "Resume recruitment."),
                EnterprisePage("Recruitment Workspace", "talentcopilot.ui.recruitment_workspace", "render_recruitment_workspace", "▦", "Pipeline, tasks and recruitment status."),
                EnterprisePage("Document Intelligence", "talentcopilot.ui.document_intelligence", "render_document_intelligence", "◫", "Extract structured data from CV documents."),
                EnterprisePage("Job Intelligence", "talentcopilot.ui.job_intelligence", "render_job_intelligence", "▤", "Extract structured role requirements."),
            ],
        ),
        "analysis": EnterpriseSection(
            "Analysis",
            "Understand candidates and compare decision signals.",
            [
                EnterprisePage("Real Matching", "talentcopilot.ui.real_matching", "render_real_matching", "◆", "Match real candidate and job text through Decision Core."),
                EnterprisePage("Real Ranking", "talentcopilot.ui.real_ranking", "render_real_ranking", "▲", "Rank multiple candidates from real text inputs."),
                EnterprisePage("Candidate Workspace", "talentcopilot.ui.candidate_workspace", "render_candidate_workspace", "◉", "Review candidates one by one."),
                EnterprisePage("Candidate Intelligence", "talentcopilot.ui.candidate_workspace_v2", "render_candidate_workspace_v2", "◎", "Decision Core candidate profile view."),
                EnterprisePage("Talent Intelligence", "talentcopilot.ui.talent_intelligence", "render_talent_intelligence", "⌕", "Understand talent coverage and sourcing readiness."),
                EnterprisePage("Comparison", "talentcopilot.ui.comparison_workspace", "render_comparison_workspace", "⇄", "Compare candidates through decision signals."),
            ],
        ),
        "interview": EnterpriseSection(
            "Interview",
            "Prepare, run and evaluate structured interviews.",
            [
                EnterprisePage("Interview Workspace", "talentcopilot.ui.interview_workspace", "render_interview_workspace", "▥", "Questions, notes, scorecards and evaluation."),
            ],
        ),
        "decision": EnterpriseSection(
            "Decision",
            "Evaluate feasibility and make collaborative hiring decisions.",
            [
                EnterprisePage("Decision Core", "talentcopilot.ui.decision_core", "render_decision_core", "◆", "Run Decision Intelligence Core."),
                EnterprisePage("Decision Core Bridge", "talentcopilot.ui.decision_core_bridge", "render_decision_core_bridge", "◇", "Bridge current sessions to Decision Core profiles."),
                EnterprisePage("Hiring Budget", "talentcopilot.ui.hiring_budget", "render_hiring_budget", "¤", "Financial feasibility without changing fit score."),
                EnterprisePage("Decision Board", "talentcopilot.ui.decision_board", "render_decision_board", "◆", "Collaborative decision review."),
                EnterprisePage("Recruiter Copilot", "talentcopilot.ui.recruiter_copilot_workspace", "render_recruiter_copilot_workspace", "✦", "Action-oriented recruiter guidance."),
            ],
        ),
        "reporting": EnterpriseSection(
            "Reporting",
            "Prepare stakeholder outputs and monitor recruitment health.",
            [
                EnterprisePage("Analytics Dashboard", "talentcopilot.ui.analytics_dashboard", "render_analytics_dashboard", "▧", "Recruitment health and KPIs."),
                EnterprisePage("Executive Reporting", "talentcopilot.ui.executive_reporting", "render_executive_reporting", "▤", "Stakeholder-ready report."),
            ],
        ),
        "administration": EnterpriseSection(
            "Administration",
            "Demo, release health, settings, design system and architecture.",
            [
                EnterprisePage("AI Platform", "talentcopilot.ui.ai_platform", "render_ai_platform", "✦", "Monitor AI infrastructure foundation."),
                EnterprisePage("Enterprise Demo Final", "talentcopilot.ui.enterprise_demo_final", "render_enterprise_demo_final", "▶", "Run the Release demo."),
                EnterprisePage("Blueprint Overview", "talentcopilot.ui.blueprint_overview", "render_blueprint_overview", "▣", "Review product architecture foundation."),
                EnterprisePage("Release 1.1 Summary", "talentcopilot.ui.release_1_1_summary", "render_release_1_1_summary", "★", "Review Release 1.1 status."),
                EnterprisePage("Release Readiness", "talentcopilot.ui.release_readiness", "render_release_readiness", "✓", "Validate release health."),
                EnterprisePage("Session Health", "talentcopilot.ui.session_health", "render_session_health", "◌", "Check session quality."),
                EnterprisePage("UI Showcase", "talentcopilot.ui.ui_showcase", "render_ui_showcase", "◧", "View design system components."),
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
