# 15 — Decision Core Orchestrator

## Purpose

The Decision Core Orchestrator is the single entry point for Decision Intelligence Core v2.

It answers:

> How do we run all intelligence engines in the correct order?

## Why it exists

Without orchestration, UI pages and services may call engines inconsistently.

The orchestrator ensures that every candidate profile is produced by the same pipeline.

## Pipeline

1. Evidence Graph
2. Evidence Intelligence
3. Fit Intelligence
4. Risk Intelligence
5. Budget Intelligence
6. Confidence Intelligence
7. Recommendation Intelligence
8. Executive Intelligence
9. Decision Trace

## Design rules

1. Workspaces should consume orchestrated CandidateDecisionProfiles.
2. Engines remain independent.
3. The orchestrator controls sequence, not scoring logic.
4. The Decision Trace must contain every major engine step.
