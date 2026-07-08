# TalentCopilot Testing Strategy

## Stable tests

`tests/stable/` contains tests that must pass for every release.

Run:

```bash
python -m pytest
```

## Legacy tests

`tests/legacy/` contains old tests from previous architectures.

They are preserved for reference but do not block current releases.

## Release tests

Each release package may add targeted tests. Once stable, those tests can be promoted to `tests/stable/`.
