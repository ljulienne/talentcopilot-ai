# Release 7.1.1 — Hiring Budget Recommendation Consistency

## Objective
Keep the official talent recommendation separate from compensation feasibility.

## Changes
- Removes fictional salary estimates when no salary expectation was provided.
- Preserves the official recruitment recommendation from the active RecruitmentSession.
- Adds explicit compensation data and budget decision statuses.
- Uses `Pending compensation data` instead of a universal `Review` fallback.
- Enables budget calculations only when real candidate salary data is available.
- Updates the Hiring Budget UI to distinguish Candidate Fit, Talent Recommendation, Compensation Data, Budget Fit and Budget Decision.

## Invariants
- Official match scores and rankings are not recalculated.
- Missing salary data never creates a synthetic budget score.
