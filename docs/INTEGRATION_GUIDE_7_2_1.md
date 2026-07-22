# Integration Guide — Release 7.2.1

## Base snapshot

- Required HEAD: `c2a79899b775df862955ccabd3593ee53530e932`
- Branch: `main`

## Installation

Run `install_release_7_2_1.py` from the extracted package in Colab.

## Validation

The installer compiles the modified modules and runs:

- `tests/test_release_7_2_1_interview_evidence_grounding.py`
- `tests/test_release_3_1_1b_interview_hotfix.py`
- `tests/test_release_3_1_1c_regressions.py`
- `tests/stable/test_stable_interview_services.py`

Run the full suite in Colab before committing.
