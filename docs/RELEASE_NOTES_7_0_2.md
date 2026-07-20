# Release 7.0.2 — Interview Intelligence Consistency & Personalization

## Fixes

- Candidate selector follows the official Mission Fit rank and displays explicit rank labels.
- Candidate selection is reset safely when the active recruitment session or candidate set changes.
- Interview reports propagate the canonical candidate identifier, name, and official rank.
- Recruitment reasoning replaces an obsolete extracted-name prefix with the canonical candidate identity.
- Interview validation focuses are generated from candidate-specific missing evidence, risks, and achievements instead of a shared generic fallback.

## Guarantees

- No score or rank is recalculated by Interview Intelligence.
- The official Recruitment Source of Truth remains authoritative.
- Employer names extracted from CV content cannot replace the canonical candidate name in the mission reasoning view.
