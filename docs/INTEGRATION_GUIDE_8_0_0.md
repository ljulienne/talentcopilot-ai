# Integration Guide — Release 8.0.0

## Required base

- Release: `7.9.2-unified-light-shell-accessibility`
- Commit: `f436173e898f41170bc8117aba3262148e4d597e`
- Branch: `main`

## Installation

Use the signed Release 8.0.0 package and run:

```bash
python install.py --repo /content/talentcopilot-ai
```

The installer validates the exact base commit and pre-install file hashes, copies the presentation-layer payload, compiles the project, runs targeted UX tests and the complete test suite, and restores the previous files if validation fails.

## Validation checklist

1. Confirm the softened navy sidebar and readable inactive navigation text.
2. Confirm the active page uses indigo/blue with a cyan left accent.
3. Confirm the main workspace is blue-gray rather than pure white.
4. Confirm Home metrics reflect real project/session data.
5. Confirm Recruitment Overview, Dashboard Perspective, Candidate Intelligence, Compensation, Interview and Compare & Decide use consistent cards and headers.
6. Confirm all PDF download controls remain visible.
7. Confirm official scores and ranking order are unchanged.
