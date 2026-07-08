# 18 — Candidate Workspace Migration

## Purpose

Candidate Workspace v2 is the first workspace designed to consume `CandidateDecisionProfile`.

It answers:

> What does the new Decision Core conclude about this candidate?

## Migration rule

The old Candidate Workspace remains available.

Candidate Workspace v2 validates the new architecture before full migration.

## Data source

```text
DecisionCoreWorkspaceBridge
        ↓
DecisionCoreOrchestrator
        ↓
CandidateDecisionProfile
        ↓
Candidate Workspace v2
```

## What it displays

- Fit Score
- Risk Level
- Confidence Score
- Recommendation
- Recommendation Rationale
- Executive Summary
- Evidence Graph preview
- Decision Trace preview
