# Release 6.3A — Explainable Scoring Engine

## Purpose
Make the canonical Mission Fit traceable without creating or overwriting a second score.

## Delivered
- `CandidateScoreBreakdown`, `ScoreDimension`, and `ScoreEvidence` contracts.
- `ExplainableScoringService` that consumes the existing official score and dimension metadata.
- Exact reconciliation of weighted contributions to the immutable Mission Fit.
- Candidate Intelligence UI section with dimension scores, weights, contributions, confidence, positives, and gaps.
- Regression tests proving that the explanation layer cannot change Mission Fit.

## Governance
Mission Fit remains the objective score stored in the active `RecruitmentSession`. Career Intelligence, Recruiter Intelligence, and Decision Ranking remain separate decision-support layers.
