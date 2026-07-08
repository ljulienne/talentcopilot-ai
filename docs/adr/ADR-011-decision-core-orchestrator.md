# ADR-011 — Decision Core Orchestrator

## Status

Accepted

## Context

Decision Core engines must run in a consistent sequence.

Calling engines manually from UI or services risks inconsistency.

## Decision

Introduce `DecisionCoreOrchestrator` as the public entry point for Decision Core v2.

## Consequences

- Workspaces can call one service.
- CandidateDecisionProfile generation becomes consistent.
- Future real-data integration becomes easier.
