# ADR-018 — Real Matching Pipeline connects extraction to Decision Core

## Status

Accepted

## Context

TalentCopilot can now extract candidate and job information separately.

The next step is to connect both into Decision Core.

## Decision

Introduce `RealMatchingPipeline` as the first end-to-end real-data matching flow.

## Consequences

- Real text inputs can produce CandidateDecisionProfiles.
- The architecture remains modular.
- Future document uploads can reuse the same pipeline.
