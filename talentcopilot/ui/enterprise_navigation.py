from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EnterprisePage:
    label: str
    module: str
    function: str
    description: str = ""
    icon: str = "•"


@dataclass(frozen=True)
class EnterpriseSection:
    title: str
    description: str
    pages: List[EnterprisePage]
    icon: str = ""

    @property
    def label(self) -> str:
        """Compatibility property used by the Streamlit shell."""
        return self.title


def _page(label, module, function, description="", icon="•"):
    return EnterprisePage(label, module, function, description, icon)


# Release Alpha exposes a decision-led product shell. Internal utilities remain
# importable through LEGACY_PAGES but are no longer primary navigation destinations.
COMMAND_PAGES = [
    _page("Executive Brief", "talentcopilot.ui.home", "render_home", "What matters and what to do next.", "✦"),
    _page("Projects", "talentcopilot.ui.project_hub", "render_project_hub", "Resume active and saved decision projects.", "▦"),
]

ANALYSIS_PAGES = [
    _page("Organization Intelligence", "talentcopilot.ui.organization_intelligence_preview", "render_organization_intelligence_preview", "Diagnose collaboration patterns from uploaded data.", "◉"),
    _page("Recruitment Workspace", "talentcopilot.ui.recruitment_workspace", "render_recruitment_workspace", icon="▣"),
    _page("Candidate Workspace", "talentcopilot.ui.candidate_workspace", "render_candidate_workspace", icon="◇"),
    _page("Comparison", "talentcopilot.ui.comparison_workspace", "render_comparison_workspace", icon="⇄"),
    _page("Analytics Dashboard", "talentcopilot.ui.analytics_dashboard", "render_analytics_dashboard", icon="▥"),
]

DECISION_PAGES = [
    _page("Interview Workspace", "talentcopilot.ui.interview_workspace", "render_interview_workspace", icon="◌"),
    _page("Hiring Budget", "talentcopilot.ui.hiring_budget", "render_hiring_budget", icon="¤"),
    _page("Decision Board", "talentcopilot.ui.decision_board", "render_decision_board", icon="✓"),
    _page("Executive Reporting", "talentcopilot.ui.executive_reporting", "render_executive_reporting", icon="▤"),
    _page("Enterprise Demo Final", "talentcopilot.ui.enterprise_demo_final", "render_enterprise_demo_final", icon="▶"),
]

ADMINISTRATION_PAGES = [
    _page("Candidate Intelligence", "talentcopilot.ui.candidate_workspace_v2", "render_candidate_workspace_v2", icon="◆"),
    _page("Interview Intelligence", "talentcopilot.ui.interview_intelligence", "render_interview_intelligence", icon="?"),
    _page("Executive Copilot", "talentcopilot.ui.executive_copilot_workspace", "render_executive_copilot_workspace", "Ask evidence-grounded executive HR questions.", "✧"),
]


LEGACY_PAGES = {
    "Product Overview": _page("Product Overview", "talentcopilot.ui.product_overview", "render_product_overview"),
    "Recruitment Command Center": _page("Recruitment Command Center", "talentcopilot.ui.command_center", "render_command_center"),
    "AI Platform": _page("AI Platform", "talentcopilot.ui.ai_platform", "render_ai_platform"),
    "Blueprint Overview": _page("Blueprint Overview", "talentcopilot.ui.blueprint_overview", "render_blueprint_overview"),
    "Decision Core": _page("Decision Core", "talentcopilot.ui.decision_core", "render_decision_core"),
    "Decision Core Bridge": _page("Decision Core Bridge", "talentcopilot.ui.decision_core_bridge", "render_decision_core_bridge"),
    "Document Intelligence": _page("Document Intelligence", "talentcopilot.ui.document_intelligence", "render_document_intelligence"),
    "Demo Experience": _page("Demo Experience", "talentcopilot.ui.demo_experience", "render_demo_experience"),
    "Hybrid Decision Board": _page("Hybrid Decision Board", "talentcopilot.ui.hybrid_decision_board", "render_hybrid_decision_board"),
    "Hybrid Intelligence": _page("Hybrid Intelligence", "talentcopilot.ui.hybrid_intelligence", "render_hybrid_intelligence"),
    "Job Intelligence": _page("Job Intelligence", "talentcopilot.ui.job_intelligence", "render_job_intelligence"),
    "LLM Extraction": _page("LLM Extraction", "talentcopilot.ui.llm_extraction", "render_llm_extraction"),
    "LLM Monitor": _page("LLM Monitor", "talentcopilot.ui.llm_monitor", "render_llm_monitor"),
    "LLM Real Upload": _page("LLM Real Upload", "talentcopilot.ui.llm_real_upload", "render_llm_real_upload"),
    "Real Matching": _page("Real Matching", "talentcopilot.ui.real_matching", "render_real_matching"),
    "Real Ranking": _page("Real Ranking", "talentcopilot.ui.real_ranking", "render_real_ranking"),
    "Real Upload": _page("Real Upload", "talentcopilot.ui.real_upload_workspace", "render_real_upload_workspace"),
    "Recruiter Copilot": _page("Recruiter Copilot", "talentcopilot.ui.recruiter_copilot_workspace", "render_recruiter_copilot_workspace"),
    "Recruitment Intelligence": _page("Recruitment Intelligence", "talentcopilot.ui.recruitment_workspace", "render_recruitment_workspace"),
    "Talent Intelligence": _page("Talent Intelligence", "talentcopilot.ui.talent_intelligence", "render_talent_intelligence"),
    "Release Summary": _page("Release Summary", "talentcopilot.ui.release_summary", "render_release_summary"),
    "Release Readiness": _page("Release Readiness", "talentcopilot.ui.release_readiness", "render_release_readiness"),
    "Release 1.1 Summary": _page("Release 1.1 Summary", "talentcopilot.ui.release_1_1_summary", "render_release_1_1_summary"),
    "Reports": _page("Reports", "talentcopilot.ui.reports_v2", "render_reports_v2"),
}


def get_enterprise_navigation() -> Dict[str, EnterpriseSection]:
    return {
        "command": EnterpriseSection("Start", "Begin with a decision-oriented AI brief.", COMMAND_PAGES, "✦"),
        "analysis": EnterpriseSection("Diagnose", "Explore recruitment and organizational signals.", ANALYSIS_PAGES, "◉"),
        "decision": EnterpriseSection("Decide", "Turn evidence into interviews, decisions and reports.", DECISION_PAGES, "✓"),
        "administration": EnterpriseSection("Explore", "Advanced and compatibility workspaces.", ADMINISTRATION_PAGES, "⋯"),
    }


def flatten_enterprise_pages():
    pages = []
    seen = set()
    for section in get_enterprise_navigation().values():
        for page in section.pages:
            if page.label not in seen:
                pages.append(page)
                seen.add(page.label)
    return pages


def get_page_by_label(label: str):
    for page in flatten_enterprise_pages():
        if page.label == label:
            return page
    return LEGACY_PAGES.get(label)
