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
