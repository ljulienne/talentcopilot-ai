# ADR-004 — Evidence Intelligence before Fit Intelligence

## Status

Accepted

## Context

Fit scores are unreliable if evidence quality is unknown.

## Decision

Evidence Intelligence must run before Fit Intelligence.

## Consequences

- Fit Intelligence can rely on evidence quality signals.
- Confidence Intelligence can use evidence readiness.
- Recommendation Intelligence can distinguish weak candidates from weak evidence.
