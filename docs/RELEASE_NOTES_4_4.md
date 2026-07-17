# TalentCopilot-AI Release 4.4

## Evidence-based candidate decision signals

Release 4.4 replaces generic comparison placeholders with deterministic recruiter-facing signals derived from the official RecruitmentSession.

### Changes

- Adds `CandidateDecisionSignalService` as the central source for recommendation, key strength and key risk.
- Preserves the official match score, AI confidence and official rank without recomputation.
- Uses required skills, extracted candidate skills, achievements and existing decision concerns when available.
- Removes the temporary Release 4.2.3 score-propagation trace from the production Recruitment Workspace.
- Adds regression tests for the canonical 86 / 66 / 30 / 25 score sequence.

### Governance

The generated signals are decision support only. A structured human review remains required before any hiring decision.
