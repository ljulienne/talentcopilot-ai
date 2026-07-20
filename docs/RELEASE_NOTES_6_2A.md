# Release 6.2A — Recruitment Source of Truth

Introduces a canonical, serializable recruitment analysis snapshot shared by Recruitment Workspace, Candidate Intelligence and Comparison.

## Highlights
- Stable candidate identity registry.
- Official Mission Fit, Decision Score and Confidence registry.
- Separate Mission Fit rank, Decision rank and Interview Priority.
- Process cache plus session-metadata persistence.
- Mutation guard detecting score/rank divergence after analysis.
- Uploaded recruitment sessions are frozen immediately after ranking.

No scoring engine is changed by this release.
