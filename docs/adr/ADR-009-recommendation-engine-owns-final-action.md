# ADR-009 — Recommendation Engine owns final action

## Status

Accepted

## Context

Earlier logic could produce inconsistent recommendations when score and recommendation were calculated separately.

## Decision

Only Recommendation Intelligence produces the final recommendation.

## Consequences

- Fit, Risk, Budget and Confidence remain separate signals.
- Contradictions such as `0% fit but Review` are prevented by explicit rules.
- Decision Trace captures the final reasoning step.
