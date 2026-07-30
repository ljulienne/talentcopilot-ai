# Changelog

## 8.2.0 — UX Clarity & Universal Risk Grounding

- Removed App health and duplicate shell-level next-action prompts from the recruiter journey.
- Rebuilt the product command bar as one balanced row for context, Search, mission status and AI Copilot.
- Separated job title and location with generic structural-label parsing.
- Added a domain-agnostic Universal Candidate Risk Grounding Engine.
- Grounded risk priority in role criticality, candidate evidence, experience, language, ownership and measurable outcomes.
- Added rich technical requirements to Candidate Intelligence when legacy skill sections are absent.
- Preserved official scores, ranks, interviews, compensation and PDF reports.


## 8.1.0 — Mockup Fidelity & Product Shell

- Added a reusable application topbar with functional page and candidate search.
- Narrowed and refined the slate-blue sidebar, introduced Material icons and removed the technical version from the brand lockup.
- Replaced the empty zero-value Home dashboard with a premium evidence-led onboarding experience.
- Preserved the data-backed dashboard when active missions or saved projects exist.
- Reduced native Streamlit chrome and aligned the global topbar, workflow rail, tabs and page content.
- Updated the visible app version to `v8.1.0`.
- Preserved official scores, ranks, evidence, interviews, compensation data and PDF reports.
## 8.0.1 — Decision Ranking Consistency Hotfix

- Corrected Decision Board to display the canonical mission rank used across Recruitment.
- Removed the stale decision-rank fallback from the Decision Board presentation model.
- Resolved Decision Board candidates by canonical candidate ID instead of candidate name.
- Aligned the candidate selector and summary card with Dashboard Perspective, Candidate Intelligence, Interview and Compare & Decide.
- Preserved official scores, decision priority, evidence, interviews, compensation and PDF reports.


## 8.0.0 — Premium Unified Experience

- Deployed the approved balanced premium UI direction across the shared application shell.
- Restored a softened navy sidebar with high-contrast integrated navigation rows.
- Harmonized the sidebar, main workspace, cards, page headers, tabs and actions with one indigo/cyan design language.
- Rebuilt Home as a real data-backed executive dashboard with active missions, candidate totals, analysis progress, priorities and project status.
- Removed inline navigation counts from button labels while preserving mission context and workflow data.
- Preserved official Talent Fit scores, ranks, evidence, interview assessments, compensation records and all PDF exports.

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

## 8.3.0 — Candidate Decision Workspace

- Consolidated pre-interview, interview, compensation, availability and final-decision context.
- Added role-requirement decision coverage with separate pre/post interview evidence.
- Added independent finalist decision matrix in Compare & Decide.
- Added final-decision owner, timestamp, decisive evidence, accepted-risk and history audit fields.
- Aligned candidate presentation rank with the canonical source-of-truth order.
- Unified Candidate Intelligence and PDF decision content without recalculating scores or ranks.

## 8.4.0 — Persistent Recruitment Projects

- Added explicit project saving and restart-safe reopening from the Projects workspace.
- Added a versioned canonical recruitment-project JSON schema.
- Preserved candidate IDs, official scores, ranks and source-of-truth fingerprints.
- Persisted interview, compensation, finalist and final-decision evidence after opt-in saving.
- Added atomic project-file writes and configurable local storage root.
- Added backward-compatible restoration of historical recruitment files.
- Added integrity rejection for persisted projects whose official scores were altered.
