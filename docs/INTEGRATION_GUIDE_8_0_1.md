# Integration Guide — Release 8.0.1

## Required base

- Release: `8.0.0-premium-unified-experience`
- Commit: `c19055e7f9fe752658d86752ae9aef5f6668896b`
- Branch: `main`

## Installation

Run the signed installer from the Release 8.0.1 package:

```bash
python install.py --repo /content/talentcopilot-ai
```

The installer validates the exact base commit and file hashes, installs the hotfix, compiles the project, runs targeted tests and the full suite, and restores the previous files if validation fails.

## Validation checklist

1. Open Dashboard Perspective and confirm the official leader and rank.
2. Open the same candidate in Candidate Intelligence and Interview & Assessment.
3. Open Compare & Decide and Decision Board.
4. Confirm the same official rank is displayed in every page.
5. Confirm the Decision Board selector and summary card show the same rank.
6. Confirm scores, evidence, compensation and PDF reports are unchanged.
