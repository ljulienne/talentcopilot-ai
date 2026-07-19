# Integration Guide — Release 4.7

1. Start from a clean `main` synchronized with GitHub.
2. Verify the base commit begins with `975caefa`.
3. Run `python install_release_4_7.py` from the extracted release package.
4. Run targeted tests:

```bash
python -m pytest -q tests/test_release_4_7_interview_intelligence_pro.py
```

5. Run the full suite:

```bash
python -m pytest -q
```

6. Launch Streamlit and validate Interview Intelligence Pro with a real active recruitment session.
7. Commit only after the tests and UI validation are green.
