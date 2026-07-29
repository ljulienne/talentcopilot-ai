# Changelog

## 7.9.1 — UI Rendering & Navigation Hotfix

- Fixed raw HTML fragments displayed in Candidate Intelligence, Interview & Assessment, and Compare & Decide.
- Hardened the shared compact page header against Markdown code-block interpretation.
- Removed the trailing finalist count from the Compare & decide sidebar label.
- Enforced blue/cyan active navigation styling for current Streamlit button markup.
- Preserved all official scores, ranks, evidence, interviews, compensation records, and PDF exports.


## 7.9.0 — Premium UX Consolidation

- Introduced a compact, consistent page header across the Recruitment journey.
- Reduced the sticky workflow shell to a concise stage rail with one recommended continuation action.
- Added compact List and Cards modes to Dashboard Perspective, defaulting to the decision-efficient List view.
- Moved advanced competency and interview charts behind progressive disclosure.
- Strengthened sidebar contrast, density and mobile responsiveness.
- Standardized button, metric, empty-state and loading-state presentation.
- Reduced duplicate primary calls to action and preserved all PDF exports.
- Preserved official scores, ranks, evidence, recommendations and compensation separation.

## 7.8.2 — Candidate Insight Grounding

- Corrected Dashboard Perspective candidate insight grounding.
- Replaced first-requirement fallbacks with candidate-specific evidence-ranked strengths and severity-ranked risks.
- Kept Dashboard Perspective and PDF insight labels aligned.
- Preserved official scores, ranks and all existing decision evidence.

# Release 7.8.1 — Recruitment Journey & Reporting

- Added permanent Home navigation and a clickable brand lockup.
- Made Dashboard Perspective the first destination after candidate analysis.
- Added whole-pool candidate review with contextual drill-down to individual profiles.
- Integrated Compensation & Budget before and after interview, including candidate expectations and offer scenarios.
- Restored recruitment, dashboard, candidate, interview, compensation and decision PDF exports.
- Moved the blue/cyan recruitment journey strip above page content and made it sticky on desktop.
- Increased sidebar navigation contrast and kept normal primary actions non-red.
- Preserved official scores, ranks, evidence and recommendations.

# Release 7.8.0 — Premium Recruitment Experience

- Replaced radio-based sidebar navigation with a modern SaaS navigation shell.
- Added configurable Digital Synergy brand identity and English slogan.
- Consolidated recruitment navigation and reduced repeated information.
- Simplified Candidate and Interview workspaces to three sections each.
- Standardized normal primary actions on blue/cyan styling.
- Preserved official scores, ranks, evidence and assessment data.

# Changelog

All notable changes to TalentCopilot are documented here.

---

## 7.7.1 — Evidence Grounding & False-Positive Guardrails

### Fixed

- Rejected names, email addresses, URLs, locations, employers and isolated job titles as transferable evidence.
- Replaced detached entity labels with complete, source-grounded CV statements.
- Added action/object/credential validation before assigning `Related evidence`.
- Added honest fallback wording when no sufficiently grounded related evidence exists.
- Regenerated embedded 7.7.0 requirement catalogues with the corrected 7.7.1 engine.
- Removed job-advert marketing text, degree conditions and section headings from competency axes.
- Merged acronym and long-form duplicates such as ICR / Individual Compensation Review.

### Improved

- SuccessFactors transferability now cites comparable HRIS implementation statements.
- ICR transferability now cites Salary Review evidence when present.
- Power BI direct evidence now prefers the strongest action statement over a tools list.
- AI transferability prioritises Data Science or ML credentials over generic dashboard evidence.
- Interview questions quote the grounded adjacent source rather than detached keywords.

### Preserved

- Domain-agnostic extraction and the multi-domain benchmark remain active.
- Official role-fit scores and ranks remain immutable.
- Saved post-interview ratings remain separate from the AI pre-interview estimate.

---

## 7.7.0 — Domain-Agnostic Requirement Intelligence

### Added

- Dynamic cross-domain extraction of exact tools, platforms, standards, methodologies and role capabilities.
- Optional source-grounded OpenAI enrichment with deterministic fallback.
- Multi-domain benchmark for software, finance, sales, supply chain, marketing and HRIS.
- Contextual evidence statuses: direct, ambiguous, related and absent.

### Changed

- Removed the HRIS-specific requirement-definition dependency from the core extractor.
- Interview questions are now driven by requirement kind, family and evidence status.
- Eligibility conditions remain outside the competency radar.

### Preserved

- Official role-fit scores and ranks remain immutable.
- The validated HRIS reference behaviour remains protected.

---

## v0.9.0-alpha

### Added

- Recruitment Dashboard
- Candidate Comparison
- Talent Pool
- Recruiter Copilot
- Semantic Search foundation
- Financial Intelligence
- Interview Intelligence
- Candidate Workspace foundation
- AI Command Center (Home)
- Design System foundation

### Improved

- Global theme
- Home page redesign
- Component architecture
- Candidate profile structure

### Fixed

- Various import issues
- UI consistency improvements
- Refactoring for future scalability

## 7.9.2 — Unified Light Shell & Accessibility

- Replaced the dark sidebar surface with a light blue-gray application shell.
- Increased navigation text contrast and font clarity.
- Converted floating white sidebar buttons into integrated navigation rows.
- Added accessible active, hover, focus, and disabled navigation states.
- Harmonized brand, mission, notice, select, expander, and recommended-next-step styling.
- Lightened shared enterprise hero surfaces.
- Preserved all business engines, scores, ranks, evidence, interviews, compensation, and PDF exports.
