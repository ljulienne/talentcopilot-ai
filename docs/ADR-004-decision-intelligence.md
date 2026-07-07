# ADR-004 — Decision Intelligence Layer

## Status

Accepted

## Context

TalentCopilot already has several intelligent layers:

- matching,
- evidence intelligence,
- competency reasoning,
- interview intelligence,
- AI governance.

However, recruiters do not only need separate signals. They need a consolidated recommendation that explains:

- whether the candidate should continue in the process,
- how reliable the recommendation is,
- what risks need human validation,
- what should be checked during interviews.

## Decision

Create an independent `DecisionEngine` that consumes existing outputs and produces a `DecisionReport`.

The engine remains deterministic and dependency-free. It can be called after the `GovernanceEngine` without modifying existing engines.

## Consequences

Positive:

- centralizes hiring recommendation logic;
- keeps AI decisions explainable;
- supports future integrations with Recruiter Copilot v2;
- prepares the platform for enterprise reporting.

Trade-offs:

- one additional orchestration layer;
- downstream UI and PDF modules must decide when to display decision outputs.
