# Integration Guide — Release 7.5.0

## Required base

Install only on:

`7.4.2-radar-visibility-bilingual-star`

The installer verifies the exact SHA-256 content of every existing file modified by this release before installation.

## Files changed

- `.talentcopilot_release`
- `app.py`
- `talentcopilot/services/recruitment_overview_service.py`
- `talentcopilot/services/recruitment_workflow_service.py`
- `talentcopilot/ui/enterprise_navigation.py`
- `talentcopilot/ui/recruitment_overview.py`
- `talentcopilot/ui/recruitment_workflow_shell.py`
- `docs/RELEASE_NOTES_7_5_0.md`
- `docs/INTEGRATION_GUIDE_7_5_0.md`
- `tests/test_release_7_5_0_visual_recruitment_overview.py`

## Validation

```bash
python -m compileall -q talentcopilot
pytest -q \
  tests/test_release_7_5_0_visual_recruitment_overview.py \
  tests/test_release_7_4_0_lot_2_recruitment_workflow_shell.py \
  tests/test_release_7_4_0_lot_3_workflow_shell_hotfix.py \
  tests/test_release_7_4_0_lot_5_premium_visual_system.py \
  tests/stable/test_stable_navigation.py \
  tests/stable/test_stable_navigation_cleanup.py \
  tests/test_navigation_registry_integrity.py
pytest -q
```

## Streamlit acceptance path

1. Complete a candidate analysis in Recruitment Workspace.
2. Use the primary action **Open visual overview**.
3. Confirm that official role-fit ranking and pool distribution are visible.
4. Open a candidate from the dashboard and confirm selection persistence.
5. Save an interview assessment.
6. Return to Recruitment Overview and select **Post-interview competencies**.
7. Confirm that interview progress and competency visuals update without changing the official rank or match score.
