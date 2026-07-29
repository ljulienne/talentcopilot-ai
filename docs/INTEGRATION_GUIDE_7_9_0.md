# Integration Guide — Release 7.9.0

## Required base

- Branch: `main`
- Base release: `7.8.2-candidate-insight-grounding`
- Base commit: `43b25ceeafb2f11df949242b6a02e7a9bd8ae3d5`

The installer verifies the branch, commit, release marker and SHA-256 of every changed file before installation.

## Installation behavior

1. Verify the exact base snapshot.
2. Verify payload and pre-install file hashes.
3. Back up every changed file.
4. Install the 7.9.0 presentation layer.
5. Compile the application.
6. Run targeted UX and regression tests.
7. Run the complete test suite.
8. Restore the previous files automatically if any step fails.

## Manual acceptance checklist

- Open every Recruitment navigation destination.
- Confirm that the workflow rail is the first visual element and remains compact.
- Confirm that the page title appears directly below the workflow rail.
- Confirm sidebar labels are readable at normal browser zoom.
- Confirm Dashboard Perspective opens in List mode and can switch to Cards.
- Confirm candidate filters and sorting remain selected after candidate drill-down.
- Confirm advanced portfolio analytics are collapsed by default.
- Confirm all six PDF exports remain downloadable.
- Confirm normal actions use blue/cyan or neutral styling, never destructive red.
- Confirm the same official scores and ranks appear before and after installation.

## Rollback

The package installer restores all changed files automatically when compilation or tests fail. Do not commit or push a failed installation.
