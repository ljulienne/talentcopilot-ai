# 22 — Real Matching Pipeline

## Purpose

The Real Matching Pipeline is the first end-to-end flow using real input text.

It connects:

- Document Intelligence;
- Job Intelligence;
- Decision Core Orchestrator.

## Flow

```text
Candidate Text
        ↓
ExtractedCandidateProfile
        ↓
DecisionCoreInput

Job Description Text
        ↓
RoleProfile
        ↓
DecisionCoreInput role fields

Decision Core
        ↓
CandidateDecisionProfile
```

## Design rules

1. Document extraction does not score.
2. Job extraction does not score.
3. Decision Core owns scores and recommendations.
4. The pipeline adapts extracted data into DecisionCoreInput.
5. UI consumes pipeline output and does not recalculate scores.
