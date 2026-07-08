from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PageDefinition:
    label: str
    module: str
    function: str
    purpose: str


@dataclass(frozen=True)
class NavigationSection:
    label: str
    description: str
    pages: List[PageDefinition]


def get_navigation_sections() -> Dict[str, NavigationSection]:
    return {
        "start": NavigationSection(
            label="Start",
            description="Create, open or understand a recruitment workflow.",
            pages=[
                PageDefinition(
                    "Home",
                    "talentcopilot.ui.home_v2",
                    "render_home_v2",
                    "Product overview and recommended workflow.",
                ),
                PageDefinition(
                    "New Recruitment",
                    "talentcopilot.ui.recruitment_wizard",
                    "render_new_recruitment",
                    "Create a recruitment context and define requirements.",
                ),
                PageDefinition(
                    "Open Recruitment",
                    "talentcopilot.ui.open_recruitment",
                    "render_open_recruitment",
                    "Resume or inspect an existing recruitment context.",
                ),
            ],
        ),
        "analyze": NavigationSection(
            label="Analyze",
            description="Understand candidates, talent pool and comparison signals.",
            pages=[
                PageDefinition(
                    "Candidates",
                    "talentcopilot.ui.candidates_v2",
                    "render_candidates_v2",
                    "Candidate-level evidence, decision and copilot details.",
                ),
                PageDefinition(
                    "Talent Pool",
                    "talentcopilot.ui.talent_pool_v2",
                    "render_talent_pool_v2",
                    "Internal talent pool and Talent Locator entry point.",
                ),
                PageDefinition(
                    "Comparison",
                    "talentcopilot.ui.comparison_v2",
                    "render_comparison_v2",
                    "Side-by-side comparison of ranked candidates.",
                ),
            ],
        ),
        "decide": NavigationSection(
            label="Decide",
            description="Review decision intelligence and recruiter guidance.",
            pages=[
                PageDefinition(
                    "Decision Center",
                    "talentcopilot.ui.dashboard_v2",
                    "render_dashboard_v2",
                    "Operational control center for active recruitment session.",
                ),
                PageDefinition(
                    "Decision Workspace",
                    "talentcopilot.ui.decision_workspace",
                    "render_decision_workspace",
                    "Governance, decision cards and explainability.",
                ),
                PageDefinition(
                    "Recruiter Copilot",
                    "talentcopilot.ui.recruiter_copilot_v2",
                    "render_recruiter_copilot_v2",
                    "Actions, alerts and interview guidance.",
                ),
            ],
        ),
        "deliver": NavigationSection(
            label="Deliver",
            description="Produce recruiter-ready reports and exports.",
            pages=[
                PageDefinition(
                    "Reports",
                    "talentcopilot.ui.reports_v2",
                    "render_reports_v2",
                    "Structured session report preview and export.",
                ),
            ],
        ),
        "admin": NavigationSection(
            label="Admin",
            description="Health, settings and product readiness.",
            pages=[
                PageDefinition(
                    "Session Health",
                    "talentcopilot.ui.session_health",
                    "render_session_health",
                    "Session quality, completeness and diagnostics.",
                ),
                PageDefinition(
                    "Settings",
                    "talentcopilot.ui.settings",
                    "render_settings",
                    "Application preferences and configuration.",
                ),
            ],
        ),
    }


def flattened_pages() -> List[PageDefinition]:
    pages = []
    for section in get_navigation_sections().values():
        pages.extend(section.pages)
    return pages
