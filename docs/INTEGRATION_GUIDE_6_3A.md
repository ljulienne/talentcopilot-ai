# Integration Guide — Release 6.3A

Install the package, run the targeted tests, then run the full test suite.

```bash
python -m pytest -q tests/test_release_6_3A_explainable_scoring.py
python -m pytest -q
```

Open Candidate Intelligence and verify that **Explainable Mission Fit** displays the official score and that the reconstructed total is identical.
