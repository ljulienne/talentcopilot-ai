# Integration Guide — Release 7.9.2

## Required base

- Branch: `main`
- Release: `7.9.1-ui-rendering-navigation-hotfix`
- Commit: `bb8d8b1b7f9f7a0eb8f5a05106c88c66a760cefa`

## Scope

This release changes the shared presentation layer only:

- `talentcopilot/ui/design_system/theme.py`

It does not change scoring, ranking, evidence, interviews, compensation, reports, or workflow services.

## Visual checks after deployment

1. Confirm every sidebar navigation label is immediately readable.
2. Confirm inactive items appear as integrated navigation rows, not floating white cards.
3. Confirm the active item uses a light blue surface, blue accent, and dark blue text.
4. Confirm the sidebar, application header, and main workspace feel like one continuous light shell.
5. Confirm mission, language, More, recommended-next-step, hover, focus, and disabled states remain readable.
6. Confirm Candidate Intelligence, Interview & Assessment, and Compare & Decide still render without raw HTML.

## Rollback

The packaged installer backs up every changed file and restores the previous version automatically if compilation or any test fails.
