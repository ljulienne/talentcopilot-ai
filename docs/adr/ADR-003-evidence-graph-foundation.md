# ADR-003 — Evidence Graph foundation

## Status

Accepted

## Context

TalentCopilot requires explainable recommendations.

Simple keyword matching is insufficient because it does not preserve reasoning or source traceability.

## Decision

Introduce an Evidence Graph as the first foundation of Decision Intelligence Core v2.

## Consequences

- Evidence can be normalized once and reused by all engines.
- Future scores can cite evidence nodes.
- Decision Trace can reference evidence IDs.
