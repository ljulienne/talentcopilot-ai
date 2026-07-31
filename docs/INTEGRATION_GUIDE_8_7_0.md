# Integration Guide — Release 8.7.0

## Base

- Release: `8.6.0-recruitment-portfolio-intelligence`
- Commit: `8c6797c16355ca3baa8a9102edc0392686cf7631`

## New components

- `talentcopilot/models/recruitment_action_center.py`
- `talentcopilot/services/recruitment_action_center.py`
- `talentcopilot/ui/recruitment_action_center.py`

## Navigation

The Action Center is available from the premium sidebar and from the Analytics attention queue.

## Persistence

Execution status is stored under:

```text
metadata.project_management.action_center.states[action_id]
```

Each entry contains only:

- status;
- update timestamp;
- actor.

The persisted project is validated before and after the metadata-only write to protect the canonical recruitment source of truth.

## Validation

Run:

```bash
python -m pytest -q tests/test_release_8_7_0_recruitment_action_center.py
python -m pytest -q
```
