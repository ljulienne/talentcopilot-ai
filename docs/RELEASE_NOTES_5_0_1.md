# Release 5.0.1 — Mission Fit Recommendation Guardrails

Base commit: `1f876b759f483a68a77a8996777a191ddd471365`

## Fixes

- Preserves Mission Fit Engine v2 weighted and explainable scoring.
- Restores the stable `Reject` decision for candidates with a severe experience shortfall and no directly matched mission concepts.
- Adds explicit critical no-fit recommendation guardrails.
- Keeps the canonical score, confidence, recommendation, risk and evidence metadata in the existing Decision Core profile.

## Validation

- Release 5.0 targeted tests pass.
- Release 5.0.1 recommendation guardrail tests pass.
- Full stable suite passes: 254 tests.
