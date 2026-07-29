# Integration Guide — Release 7.9.1

## Required base

- Branch: `main`
- Release: `7.9.0-premium-ux-consolidation`
- Commit: `03a4dbe6a23a79e57b79b91e7dd1a9b7ec05e601`

## Scope

This hotfix changes presentation files only:

- `talentcopilot/ui/design_system/components.py`
- `talentcopilot/ui/design_system/theme.py`
- `talentcopilot/ui/premium_sidebar.py`

No scoring, ranking, evidence, interview, compensation, or PDF service is changed.

## Visual checks after deployment

1. Open Candidate Intelligence and confirm that the status `Evidence-led review` appears as a badge, with no raw HTML.
2. Open Interview & Assessment and confirm that `Human assessment` appears as a badge, with no raw HTML.
3. Open Compare & Decide and confirm that `Human-owned decision` appears as a badge, with no raw HTML.
4. Confirm the sidebar label reads `Compare & decide` without a trailing number.
5. Confirm the active sidebar item uses the blue/cyan gradient rather than red.

## Rollback

The packaged installer backs up every changed file and restores the previous files automatically if compilation or any test fails.
