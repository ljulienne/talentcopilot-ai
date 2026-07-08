# 23 — Real Ranking Pipeline

## Purpose

The Real Ranking Pipeline ranks multiple candidates against one real job description.

## Flow

```text
Job Description
        ↓
RoleProfile
        ↓
Candidates
        ↓
Real Matching Pipeline
        ↓
CandidateDecisionProfiles
        ↓
Ranking Rules
```

## Ranking principles

1. Recommendation is the first-level decision signal.
2. Fit Score remains independent.
3. Confidence is used to avoid over-ranking uncertain analyses.
4. Risk level affects ranking, but does not rewrite fit.
5. Budget fit is considered as feasibility, not candidate quality.

## Future evolution

This pipeline will later support:

- 50 uploaded CVs;
- file upload batch processing;
- ranking explanations;
- weighting simulation;
- recruiter-adjusted priorities.
