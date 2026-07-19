# Integration Guide — Release 6.0B.3

## Install

Run the package installer from the repository baseline declared in the release
notes. The installer refuses unrelated working-tree changes.

## Validation

The installer performs:

1. exact HEAD verification;
2. Python compilation of the adapter and migrated workspace;
3. targeted Release 6.0B.3 tests;
4. Release 6.0B.2 workspace-engine regression tests;
5. `git diff --check`;
6. working-tree and diff summaries.

It does not commit or push.

## Manual UI check

After installation, launch Streamlit and open Recruitment Mission.

Confirm:

- the upload panel still works;
- the mission hero uses the Enterprise Workspace visual shell;
- official candidate scores and ranks are unchanged;
- Ranking opens by default;
- Overview, Reasoning, Comparison, Interview, Decision and Report still render.
