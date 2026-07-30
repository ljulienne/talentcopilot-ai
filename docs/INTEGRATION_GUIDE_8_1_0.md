# Integration Guide — Release 8.1.0

## Required base

- Release: `8.0.1-decision-ranking-consistency-hotfix`
- Commit: `b64b2f9ad7d71e6344565b335065de3e22b536ac`
- Branch: `main`

## Installation

Run the packaged installer from Colab:

```bash
python install.py --repo /content/talentcopilot-ai
```

The installer validates the exact base commit and file hashes, installs the presentation changes, compiles the project, runs targeted tests and the full suite, and restores the previous files on failure.

## Visual validation checklist

1. Confirm the native Streamlit toolbar is reduced and the TalentCopilot topbar is visible.
2. Use global search to open `Dashboard Perspective` and a candidate profile.
3. Confirm the sidebar is narrower, the logo is readable and navigation uses consistent icons.
4. With no mission, confirm Home displays onboarding rather than four zero-valued metric cards.
5. With an active mission, confirm real metrics, priorities and projects remain data-backed.
6. Open all Recruitment pages and confirm the workflow rail sits below the topbar.
7. Confirm official scores, ranks, evidence and PDF exports are unchanged.
