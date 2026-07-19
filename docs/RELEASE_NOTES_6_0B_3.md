# Release 6.0B.3 — Recruitment Mission Enterprise Workspace Migration

## Official baseline

`d558ebd65a63fc8ee6df0fa1576cc505081fb5d8`

## Purpose

Migrate the existing Recruitment Mission page to the reusable Enterprise
Workspace Engine introduced in Release 6.0B.2.

## Architecture

`RecruitmentSession`
→ `RecruitmentMissionState`
→ `build_enterprise_workspace_model`
→ `EnterpriseWorkspaceModel`
→ `render_enterprise_workspace`

## Guarantees

- No matching logic is changed.
- No official score is recalculated.
- No official rank is recalculated.
- Existing mission section renderers remain in use.
- The adapter is presentation-only and Streamlit-independent.
- The old mission layout module remains in the repository for compatibility,
  but the migrated workspace no longer imports or uses it.

## Files

- `talentcopilot/recruitment/mission/enterprise_adapter.py`
- `talentcopilot/recruitment/mission/workspace.py`
- `tests/test_release_6_0b_3_recruitment_mission_workspace.py`
- `docs/RELEASE_NOTES_6_0B_3.md`
