# Integration Guide — Release 7.7.1

## Required base

- Branch: `main`
- Commit: `1fcbb967a155cc6da60607129c835470527bc88e`
- Release marker: `7.7.0-domain-agnostic-requirement-intelligence`

## Installation behaviour

The installer verifies the exact base commit, release marker and SHA-256 hashes of all replaced files. It creates a backup, installs the payload, compiles the package, runs targeted tests and then runs the full test suite. Any failure restores the original files.

## Existing recruitment sessions

Job catalogues embedded with engine version `7.7.0` are intentionally regenerated from the job offer text. Existing competency matrices are synchronised:

- corrected requirements become active;
- removed noisy requirements remain in history but are archived from the active radar;
- interview-added competencies are unchanged;
- existing interviewer ratings remain attached to requirements whose stable identifier is unchanged.

## Streamlit verification

1. Reopen the HRIS test recruitment session.
2. Confirm that contact details and job titles no longer appear under related evidence.
3. Confirm that SuccessFactors cites SeditWeb2, Premium RH or TAPPLENT implementation statements.
4. Confirm that ICR cites the Salary Review module statement.
5. Confirm that Power BI cites the launch statement.
6. Confirm that the active radar has no `Data Functional`, `About LVMH`, `Bac+5`, duplicate `ICR` or duplicate `Individual Compensation` axis.
7. Confirm that official scores and ranks are unchanged.
