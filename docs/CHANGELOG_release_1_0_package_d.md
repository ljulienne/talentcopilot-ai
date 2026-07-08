# Release 1.0 Package D — Repository Cleanup & Stable Test Suite

## Added

- Stable test suite under `tests/stable/`.
- Legacy test quarantine under `tests/legacy/`.
- `pytest.ini` configuration to run stable tests by default.
- Cleanup report in `docs/cleanup/legacy_tests_report.md`.
- Developer testing guide.

## Improved

- Running `pytest` no longer triggers obsolete import errors from legacy tests.
- Release validation becomes faster and more predictable.
