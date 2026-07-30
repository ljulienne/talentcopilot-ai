# Release 8.2.0 — UX Clarity & Universal Risk Grounding

## Base

- Release: `8.1.0-mockup-fidelity-product-shell`
- Commit: `73cecad689c7df497699743cd8838b4cb9017344`

## UX clarity

- Removed the technical `App health` expander from the recruiter-facing sidebar.
- Removed the sidebar `Next up` recommendation and the workflow continuation row.
- Kept the workflow rail as a compact progress indicator while each page owns one contextual next action.
- Redesigned the product top command bar into one balanced horizontal surface for page context, Search, active mission and AI Copilot.
- Preserved the approved softened navy sidebar and balanced light blue-gray workspace.

## Job description grounding

- Added deterministic separation between role title and location.
- Structural field labels such as `Location`, `Job Description`, `Position`, `Profile` and their French equivalents are no longer appended to the role title.
- The uploaded LVMH example now resolves to `HRIS Manager` with `Paris (75)` stored separately as the location.
- The logic is generic and tested with a non-HRIS sales role.

## Universal Candidate Risk Grounding Engine

- Added a domain-agnostic engine that ranks candidate risks from real role requirements and candidate evidence.
- Uses criticality, evidence depth, experience gaps, language gaps, ownership evidence and measurable outcomes.
- Generates requirement-specific explanations, evidence bases and interview validation questions.
- Uses the rich technical requirement catalog when a job description does not contain a literal `Skills` section.
- Does not hard-code HRIS, SAP SuccessFactors, Workday or any other job-family technology.
- Replaces the unconditional `Personal ownership is unclear` fallback with contextual, evidence-grounded risk wording.

## Data integrity

This release does not recalculate or modify:

- official Talent Fit scores;
- official mission ranks;
- decision ranks or interview priority;
- candidate evidence;
- interview assessments;
- compensation and budget records;
- PDF reports.

## Validation

- 8 release-specific tests;
- previous UX, rendering, dashboard and candidate grounding regression tests;
- 254 tests in the complete repository suite.
