# Release 8.5.0 — Recruitment Portfolio & Lifecycle

## Purpose

Release 8.5.0 turns restart-safe recruitment projects into a usable portfolio. Recruiters can find, prioritise, reopen and archive saved decision workspaces without changing candidate scores, ranks or evidence.

## Added

- Search across project name, role title, location and owner.
- Lifecycle filters for Draft, Analyzing, Review, Interview, Decision ready, Decided and Archived.
- Sorting by recent activity, age, name, progress or priority.
- Project owner, display name and priority management.
- Safe archive and reopen actions with decision evidence retained.
- Portfolio metrics for open projects, candidates, decision-ready projects and archives.
- Lifecycle-aware Active Projects metrics on the Executive Brief.
- Visible application version aligned to `v8.5.0`.

## Data and governance

Project-management metadata is stored separately from the canonical candidate analysis. Portfolio edits are validated before and after storage against the persisted Recruitment Source of Truth. No score, rank, candidate identity, interview evidence, compensation input or decision history is recalculated.

## Compatibility

- Existing Release 8.4.0 project files remain loadable.
- Projects without portfolio metadata receive safe defaults.
- The persistence layer remains local JSON storage. A production multi-user deployment still requires an external database or durable object store.
