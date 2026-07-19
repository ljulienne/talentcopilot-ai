# Release 6.0B.3.1 — Universal Matching Regression Fix

Baseline: `4465a22b7a11d57c9ba824a6d14e524f9d4b6e81`

## Root cause

The official score was flattened for non-sales jobs because:

1. Mission Fit v2 primarily modeled Sales/Operations/Engineering concepts.
2. Comparative Ranking used sales-specific title and textile rules.
3. Calibration applied sales-oriented commercial, APAC and leadership caps to
   every job family.

This produced near-identical HRIS scores even for materially different CVs.

## Changes

- Universal deterministic Mission Fit ontology.
- HRIS/SIRH, Finance, Engineering, Supply Chain, Data, Marketing and HR families.
- French and English HRIS vocabulary.
- Job-aware comparative ranking.
- Continuous non-sales calibration dominated by Mission Fit.
- Existing Sales Manager calibration contract preserved.
- Cache schema bumped so old browser-session scores are not restored.
- Cross-domain ranking tests.

No candidate-name rule or job-specific hard-coded expected score is introduced.
