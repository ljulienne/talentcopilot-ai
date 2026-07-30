# Integration Guide — Release 8.2.0

## Required base

- Release: `8.1.0-mockup-fidelity-product-shell`
- Commit: `73cecad689c7df497699743cd8838b4cb9017344`
- Branch: `main`

## Installation

Run the packaged installer from Colab:

```bash
python install.py --repo /content/talentcopilot-ai
```

The installer validates the exact base commit and source hashes, installs the release, compiles the project, runs targeted tests and the full suite, and restores the previous files if validation fails.

## Functional validation checklist

1. Confirm `App health` is absent from the business sidebar.
2. Confirm the sidebar no longer displays a separate `Next up` action.
3. Confirm the workflow strip shows progress only and the page body contains the single contextual action.
4. Confirm the top command bar presents page context, Search, active mission and AI Copilot on one balanced row.
5. Upload the HRIS Manager offer and confirm the title is `HRIS Manager`, not `HRIS Manager Location`.
6. Confirm `Paris (75)` is stored separately as the job location.
7. Review several candidates and confirm risks refer to different evidenced requirements when their profiles differ.
8. Confirm no score or official rank changes after the release.
9. Confirm existing PDF downloads, interview records and compensation data remain available.
