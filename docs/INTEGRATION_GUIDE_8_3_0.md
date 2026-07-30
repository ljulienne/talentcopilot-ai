# Integration Guide — Release 8.3.0

## Required base

- Branch: `main`
- Release: `8.2.0-ux-clarity-universal-risk-grounding`
- Commit: `ae9d4a8af35b2137d06bc226080369ecc3eff233`

## Installation contract

The installer verifies:

1. exact Git HEAD;
2. exact release marker;
3. clean tracked working tree;
4. hashes of every file replaced from the base snapshot;
5. hashes of every package payload file;
6. Python compilation;
7. targeted release and regression tests;
8. the complete test suite;
9. final installed hashes and release marker.

Any failure triggers automatic rollback.

## Manual validation after Streamlit deployment

1. Open **Dashboard Perspective**, select a candidate and open **Candidate Intelligence**.
2. Confirm that official Talent Fit and rank are unchanged.
3. Confirm that the Overview tab displays:
   - Decision journey;
   - demonstrated strengths and candidate-specific risks;
   - role-requirement coverage with separate pre/post interview levels;
   - compensation and availability context.
4. Save an interview assessment and confirm that the interview stage changes
   without changing Talent Fit.
5. Open **Compare & Decide** and verify the independent decision columns.
6. Open **Decision Board**, record owner, decisive evidence, accepted risks and
   rationale, then verify the audit history.
7. Export candidate and comparison PDFs and compare them with the UI values.
