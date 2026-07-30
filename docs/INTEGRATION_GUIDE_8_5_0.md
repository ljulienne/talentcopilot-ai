# Integration Guide — Release 8.5.0

## Base

- Expected release: `8.4.0-persistent-recruitment-projects`
- Expected commit: `edd70f3d7fbaf930159a0469899802f4863af37a`
- Target release: `8.5.0-recruitment-portfolio-lifecycle`

## Installation contract

The installer requires:

1. the `main` branch;
2. the exact base commit and release marker;
3. a clean tracked working tree;
4. matching pre-install hashes for every replaced file;
5. matching payload hashes;
6. successful Python compilation;
7. successful targeted regression tests;
8. a successful full test suite.

Any failure restores the previous repository files automatically.

## Main components

- `talentcopilot/services/recruitment_project_portfolio.py`
  - portfolio summaries;
  - lifecycle derivation;
  - search, filtering, sorting and metrics;
  - owner, display-name and priority metadata;
  - archive and reopen operations.
- `talentcopilot/ui/project_hub.py`
  - portfolio dashboard and project-management controls.
- `talentcopilot/storage/recruitment_store.py`
  - exposes safe project metadata to portfolio listings.
- `talentcopilot/services/recruitment_project_persistence.py`
  - carries compact workflow state into project-management metadata.
- `talentcopilot/ui/executive_briefing.py`
  - excludes archived projects from active portfolio metrics.

## Source-of-truth protection

Portfolio operations load and validate the saved recruitment before mutation, write only project-management metadata, then validate the saved project again. Official candidate IDs, Talent Fit scores, decision scores and ranks remain immutable.

## Post-deployment visual checks

After Streamlit redeploy:

- open **Projects**;
- verify search, stage filter, sort and Archived toggle;
- edit a project name, owner and priority;
- archive and reopen a saved project;
- reopen the project and confirm scores, ranks, interviews, compensation and final-decision history are unchanged;
- verify the Executive Brief excludes archived projects from Active missions.
