from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from talentcopilot.ui.design_system.components import page_header
from talentcopilot.ui.premium_sidebar import resolve_recruitment_destinations


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_SOURCE = (ROOT / "talentcopilot/ui/design_system/components.py").read_text(encoding="utf-8")
SIDEBAR_SOURCE = (ROOT / "talentcopilot/ui/premium_sidebar.py").read_text(encoding="utf-8")
THEME_SOURCE = (ROOT / "talentcopilot/ui/design_system/theme.py").read_text(encoding="utf-8")
CANDIDATE_SOURCE = (ROOT / "talentcopilot/ui/candidate_workspace.py").read_text(encoding="utf-8")
INTERVIEW_SOURCE = (ROOT / "talentcopilot/ui/interview_intelligence.py").read_text(encoding="utf-8")
COMPARISON_SOURCE = (ROOT / "talentcopilot/ui/comparison_workspace.py").read_text(encoding="utf-8")


def test_shared_page_header_emits_one_non_indented_html_fragment(monkeypatch):
    calls = []

    def markdown(body, **kwargs):
        calls.append((body, kwargs))

    monkeypatch.setitem(sys.modules, "streamlit", SimpleNamespace(markdown=markdown))
    page_header(
        "Candidate Intelligence",
        "Review the decision first.",
        eyebrow="Recruitment · Candidate detail",
        metadata=("Rank #1", "85% Talent Fit"),
        status="Evidence-led review",
    )

    assert len(calls) == 1
    body, kwargs = calls[0]
    assert kwargs == {"unsafe_allow_html": True}
    assert "\n" not in body
    assert body.startswith('<section class="tc-page-header">')
    assert body.endswith("</section>")
    assert body.count('<section class="tc-page-header">') == 1
    assert body.count("</section>") == 1
    assert body.count('<div class="tc-page-header-main">') == 1
    assert body.count('<span class="tc-page-status">Evidence-led review</span>') == 1
    assert "</div><span" in body


def test_page_header_escapes_user_visible_content(monkeypatch):
    calls = []
    monkeypatch.setitem(
        sys.modules,
        "streamlit",
        SimpleNamespace(markdown=lambda body, **kwargs: calls.append(body)),
    )
    page_header("<Candidate>", "A & B", status="<review>")
    body = calls[0]
    assert "&lt;Candidate&gt;" in body
    assert "A &amp; B" in body
    assert "&lt;review&gt;" in body
    assert "<Candidate>" not in body


def test_all_affected_pages_use_the_shared_safe_header():
    for source, status in (
        (CANDIDATE_SOURCE, "Evidence-led review"),
        (INTERVIEW_SOURCE, "Human assessment"),
        (COMPARISON_SOURCE, "Human-owned decision"),
    ):
        assert "page_header(" in source
        assert f'status="{status}"' in source
    assert 'header_html = "".join(' in COMPONENT_SOURCE


def test_compare_navigation_omits_the_inline_finalist_count():
    items = resolve_recruitment_destinations(
        None,
        current_page="Comparison",
        include_journey_v2=True,
    )
    decide = next(item for item in items if item.key == "decide")
    assert decide.label == "Compare & decide"
    assert decide.badge == ""


def test_active_navigation_supports_current_streamlit_button_markup():
    assert 'button[data-testid="stBaseButton-primary"]' in THEME_SOURCE
    assert 'background:linear-gradient(105deg,rgba(37,99,235,.96),rgba(6,182,212,.82)) !important' in THEME_SOURCE
    active_rule = THEME_SOURCE.split(
        '[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]',
        1,
    )[1].split("}}", 1)[0]
    assert "#FF4B4B" not in active_rule
    assert "red" not in active_rule.lower()


def test_hotfix_does_not_touch_business_engines():
    release_notes = (ROOT / "docs/RELEASE_NOTES_7_9_1.md").read_text(encoding="utf-8")
    assert "Official Talent Fit scores and ranks" in release_notes
    assert "PDF exports" in release_notes
