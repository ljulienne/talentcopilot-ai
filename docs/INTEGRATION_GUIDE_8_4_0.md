# Integration Guide — Release 8.4.0

## Required base

- Branch: `main`
- Release: `8.3.0-candidate-decision-workspace`
- Commit: `cdfa1a3a00a3d0e4c6d98ca4d555588fa79f5275`

## Installation contract

The installer verifies:

1. exact Git HEAD;
2. exact release marker;
3. clean tracked working tree;
4. hashes of every replaced base file;
5. hashes of every package payload file;
6. Python compilation;
7. targeted release and regression tests;
8. the complete test suite;
9. final installed hashes and release marker.

Any failure triggers automatic rollback.

## Manual validation after Streamlit deployment

1. Run or reopen a real uploaded recruitment.
2. Open **Projects** and confirm that the active project is described as
   browser-session only before saving.
3. Select **Save project**.
4. Change one interview evaluation, compensation input or final-decision field.
5. Return to **Projects** and confirm that the project is marked as saved.
6. Clear the active Streamlit session or restart the app runtime without
   deleting the configured data directory.
7. Open **Projects**, reopen the saved recruitment and verify:
   - candidate identities;
   - official scores and ranks;
   - selected finalists;
   - interview evidence;
   - compensation and availability;
   - final-decision history.
8. Confirm that a sample/demo recruitment is not silently persisted.

## Storage configuration

The default storage directory is `data/recruitments`. A different local root
can be configured before launching Streamlit:

```bash
export TALENTCOPILOT_DATA_DIR=/path/to/persistent/data
```

For production or multi-user deployment, replace the local JSON adapter with a
secured database/object-storage implementation before treating persistence as
durable infrastructure.
