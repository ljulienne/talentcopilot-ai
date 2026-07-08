# 16 — Decision Core UI Integration

## Purpose

The Decision Core UI Integration makes the new Decision Intelligence Core visible in the application.

It is not yet a replacement for all existing workspaces.

It is a diagnostic and demonstration page showing that the new architecture works end-to-end.

## What the page shows

- CandidateDecisionProfile
- Fit Score
- Risk Level
- Confidence Score
- Budget Fit
- Final Recommendation
- Executive Summary
- Engine Status
- Decision Trace

## Design rule

The UI must consume the orchestrator output.

It must not recalculate Decision Core scores.
