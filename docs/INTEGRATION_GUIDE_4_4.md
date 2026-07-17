# Release 4.4 Integration Guide

1. Confirm `main` is at `e0f6e4a58c86bb10471d5df729bcdb154b54d2bb` and the worktree is clean.
2. Extract the release ZIP at the repository root, preserving paths.
3. Run `python -m pytest -q tests/test_release_4_4_evidence_based_decision_signals.py tests/stable/test_stable_comparison_workspace.py tests/test_release_3_3_official_match_ux.py`.
4. Run the full suite with `python -m pytest -q`.
5. Review the Streamlit Recruitment Workspace and Comparison output.
6. Commit and push only after validation.
