# Integration Guide — Release 4.6

## Base requirement
Install on a clean `main` branch containing the validated Release 4.5A commit (`Release 4.5A - Executive Decision Intelligence`).

## Files
- `talentcopilot/services/executive_decision_center_service.py`
- `talentcopilot/services/executive_decision_pdf_service.py`
- `talentcopilot/ui/candidate_workspace.py`
- `tests/test_release_4_6_executive_decision_center.py`
- release documentation

## Validation
Run:

```bash
python -m pytest -q tests/test_release_4_6_executive_decision_center.py
python -m pytest -q
```

Then verify Candidate Intelligence in Streamlit, including PDF download and unchanged official scores/ranks.
