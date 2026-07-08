# 07 — CandidateDecisionProfile Contract

## Purpose

`CandidateDecisionProfile` is the future single source of truth for candidate intelligence.

## Contract

A CandidateDecisionProfile must include:

- candidate identity;
- recruitment context;
- evidence graph;
- decision trace;
- fit section;
- risk section;
- budget section;
- interview section;
- confidence section;
- recommendation section.

In Package A, only the foundation fields are implemented.

## Rule

Workspaces may consume a CandidateDecisionProfile.

Workspaces must not mutate core intelligence outputs directly.

## Future evolution

The object will be progressively enriched by:

- Evidence Intelligence;
- Fit Intelligence;
- Competency Intelligence;
- Risk Intelligence;
- Budget Intelligence;
- Interview Intelligence;
- Confidence Intelligence;
- Recommendation Intelligence.
