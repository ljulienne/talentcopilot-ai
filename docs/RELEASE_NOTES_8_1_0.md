# Release 8.1.0 — Mockup Fidelity & Product Shell

## Base

- Release: `8.0.1-decision-ranking-consistency-hotfix`
- Commit: `b64b2f9ad7d71e6344565b335065de3e22b536ac`

## Objective

Rebuild the shared Streamlit presentation shell so the live product is materially closer to the approved premium SaaS mockup, rather than applying another isolated color layer.

## Delivered

- reusable global product topbar;
- functional search for existing pages and canonical candidate profiles;
- narrower integrated sidebar with Material icons and accessible contrast;
- compact, readable brand lockup without an obsolete technical version label;
- premium zero-state onboarding when no mission or project exists;
- existing data-backed Home dashboard retained for active missions and saved projects;
- workflow rail moved below the global topbar and made non-sticky on narrower screens;
- reduced native Streamlit toolbar footprint;
- balanced slate-blue, blue-gray, ivory, indigo and cyan visual system;
- visible application version aligned to `v8.1.0`.

## Data integrity

No matching, ranking, evidence, interview, compensation, recommendation or PDF engine is changed. Search opens existing canonical pages and synchronizes the workflow candidate by immutable candidate ID.

## Validation

- Release-specific shell and search tests;
- prior UX, navigation, rendering and ranking regression tests;
- full repository test suite.
