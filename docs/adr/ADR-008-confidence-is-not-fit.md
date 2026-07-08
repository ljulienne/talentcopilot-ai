# ADR-008 — Confidence is not Fit

## Status

Accepted

## Context

Traditional matching tools often present scores as if they were certain.

This creates false confidence when evidence is weak.

## Decision

TalentCopilot separates Fit Score from Confidence Score.

## Consequences

- The system can say: strong candidate, weak evidence.
- Interview questions can target confidence gaps.
- Recommendation Engine can avoid overconfident outputs.
