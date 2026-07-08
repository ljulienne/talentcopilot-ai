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
        "command": EnterpriseSection("Command", "Start here.", [
            EnterprisePage("Product Overview", "talentcopilot.ui.product_overview", "render_product_overview", "◇"),
            EnterprisePage("Recruitment Command Center", "talentcopilot.ui.command_center", "render_command_center", "⌂"),
        ]),
        "recruitment": EnterpriseSection("Recruitment", "Recruitment workflows.", [
            EnterprisePage("New Recruitment", "talentcopilot.ui.recruitment_wizard", "render_new_recruitment", "＋"),
            EnterprisePage("Open Recruitment", "talentcopilot.ui.open_recruitment", "render_open_recruitment", "▣"),
            EnterprisePage("Recruitment Workspace", "talentcopilot.ui.recruitment_workspace", "render_recruitment_workspace", "▦"),
            EnterprisePage("LLM Real Upload", "talentcopilot.ui.llm_real_upload", "render_llm_real_upload", "⇪"),
            EnterprisePage("Real Upload", "talentcopilot.ui.real_upload_workspace", "render_real_upload_workspace", "⇧"),
            EnterprisePage("Document Intelligence", "talentcopilot.ui.document_intelligence", "render_document_intelligence", "◫"),
            EnterprisePage("Job Intelligence", "talentcopilot.ui.job_intelligence", "render_job_intelligence", "▤"),
        ]),
        "analysis": EnterpriseSection("Analysis", "Candidate analysis.", [
            EnterprisePage("Hybrid Intelligence", "talentcopilot.ui.hybrid_intelligence", "render_hybrid_intelligence", "✧"),
            EnterprisePage("Real Matching", "talentcopilot.ui.real_matching", "render_real_matching", "◆"),
            EnterprisePage("Real Ranking", "talentcopilot.ui.real_ranking", "render_real_ranking", "▲"),
            EnterprisePage("Candidate Workspace", "talentcopilot.ui.candidate_workspace", "render_candidate_workspace", "◉"),
            EnterprisePage("Candidate Intelligence", "talentcopilot.ui.candidate_workspace_v2", "render_candidate_workspace_v2", "◎"),
            EnterprisePage("Talent Intelligence", "talentcopilot.ui.talent_intelligence", "render_talent_intelligence", "⌕"),
            EnterprisePage("Comparison", "talentcopilot.ui.comparison_workspace", "render_comparison_workspace", "⇄"),
        ]),
        "interview": EnterpriseSection("Interview", "Interview workflows.", [
            EnterprisePage("Interview Intelligence", "talentcopilot.ui.interview_intelligence", "render_interview_intelligence", "✦"),
            EnterprisePage("Interview Workspace", "talentcopilot.ui.interview_workspace", "render_interview_workspace", "▥"),
        ]),
        "decision": EnterpriseSection("Decision", "Decision workflows.", [
            EnterprisePage("Decision Core", "talentcopilot.ui.decision_core", "render_decision_core", "◆"),
            EnterprisePage("Decision Core Bridge", "talentcopilot.ui.decision_core_bridge", "render_decision_core_bridge", "◇"),
            EnterprisePage("Hiring Budget", "talentcopilot.ui.hiring_budget", "render_hiring_budget", "¤"),
            EnterprisePage("Decision Board", "talentcopilot.ui.decision_board", "render_decision_board", "◆"),
            EnterprisePage("Recruiter Copilot", "talentcopilot.ui.recruiter_copilot_workspace", "render_recruiter_copilot_workspace", "✦"),
        ]),
        "reporting": EnterpriseSection("Reporting", "Reporting.", [
            EnterprisePage("Analytics Dashboard", "talentcopilot.ui.analytics_dashboard", "render_analytics_dashboard", "▧"),
            EnterprisePage("Executive Reporting", "talentcopilot.ui.executive_reporting", "render_executive_reporting", "▤"),
        ]),
        "administration": EnterpriseSection("Administration", "Administration.", [
            EnterprisePage("LLM Monitor", "talentcopilot.ui.llm_monitor", "render_llm_monitor", "◷"),
            EnterprisePage("LLM Extraction", "talentcopilot.ui.llm_extraction", "render_llm_extraction", "✧"),
            EnterprisePage("AI Platform", "talentcopilot.ui.ai_platform", "render_ai_platform", "✦"),
            EnterprisePage("Enterprise Demo Final", "talentcopilot.ui.enterprise_demo_final", "render_enterprise_demo_final", "▶"),
            EnterprisePage("Blueprint Overview", "talentcopilot.ui.blueprint_overview", "render_blueprint_overview", "▣"),
            EnterprisePage("Release 1.1 Summary", "talentcopilot.ui.release_1_1_summary", "render_release_1_1_summary", "★"),
            EnterprisePage("Release Readiness", "talentcopilot.ui.release_readiness", "render_release_readiness", "✓"),
            EnterprisePage("Session Health", "talentcopilot.ui.session_health", "render_session_health", "◌"),
            EnterprisePage("UI Showcase", "talentcopilot.ui.ui_showcase", "render_ui_showcase", "◧"),
            EnterprisePage("Settings", "talentcopilot.ui.settings", "render_settings", "⚙"),
        ]),
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
