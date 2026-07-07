# ADR-010 — Product Readiness Layer

## Status

Accepted

## Context

TalentCopilot now has an enterprise integration pipeline and recruiter workflow. Before adding more advanced features, the product needs an internal readiness layer to verify whether the application is demo-ready.

## Decision

Create a Product Readiness layer that evaluates:

- session availability;
- candidate analysis coverage;
- workflow status;
- blockers;
- version information;
- UI readiness.

## Consequences

Positive:
- improves demo preparation;
- helps detect incomplete workflows;
- creates a quality gate before future sprints.

Trade-offs:
- readiness is initially heuristic and deterministic.
