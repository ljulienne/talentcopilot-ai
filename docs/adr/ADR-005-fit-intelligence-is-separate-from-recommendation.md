# ADR-005 — Fit Intelligence is separate from Recommendation Intelligence

## Status

Accepted

## Context

A high-fit candidate may still be too expensive, unavailable or risky.

A low-fit candidate may be affordable, but should not be recommended only because of cost.

## Decision

Fit Intelligence produces only fit-related outputs.

Recommendation Intelligence will combine fit with budget, risk, confidence and policy.

## Consequences

- Fit Score remains interpretable.
- Recommendation can explain trade-offs.
- Contradictions such as `0% fit but Review` can be prevented by explicit recommendation rules.
