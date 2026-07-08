# 17 — Workspace Migration Bridge

## Purpose

The Workspace Migration Bridge allows existing workspaces to consume Decision Core outputs progressively.

It answers:

> How do we migrate the UI to Decision Core without breaking the current demo?

## Migration strategy

1. Keep existing workspaces stable.
2. Add Decision Core Bridge as a diagnostic page.
3. Convert active recruitment session candidates into DecisionCoreInput.
4. Produce CandidateDecisionProfiles.
5. Gradually replace old workspace data sources.

## Design rules

1. The bridge adapts existing session objects.
2. The bridge does not contain scoring logic.
3. The bridge calls the DecisionCoreOrchestrator.
4. Workspaces should eventually read CandidateDecisionProfile.
