# Release 7.9.1 — UI Rendering & Navigation Hotfix

## Purpose

Correct visual regressions introduced by the compact premium header and sidebar navigation in Release 7.9.0.

## Fixed

- Candidate Intelligence no longer exposes closing HTML tags as visible text.
- Interview & Assessment no longer exposes closing HTML tags as visible text.
- Compare & Decide no longer exposes closing HTML tags as visible text.
- The shared `page_header` now emits one compact, non-indented HTML fragment, preventing Markdown from treating nested tags as a code block.
- The trailing finalist count is removed from the `Compare & decide` sidebar label.
- Active sidebar navigation is forced to the blue/cyan premium treatment across both legacy and current Streamlit button DOM variants.

## Preserved

- Official Talent Fit scores and ranks.
- Evidence grounding and candidate insights.
- Interview assessments and compensation data.
- PDF exports and workflow state.
- Recruitment navigation and page routes.

## Validation

The release adds regression tests for shared header rendering, navigation badge behavior, and resilient active-button styling, then runs the complete historical test suite.
