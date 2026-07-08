# ADR-002 — Fit and Budget separation

## Status

Accepted

## Context

A candidate can be an excellent fit but financially difficult to hire.

If budget directly reduces Fit Score, the system hides the real trade-off.

## Decision

Candidate Fit and Budget Fit must remain separate.

## Consequences

- Strong but expensive candidates receive compensation review recommendations.
- Weak candidates remain weak even if affordable.
- The Recommendation Engine combines both dimensions explicitly.
