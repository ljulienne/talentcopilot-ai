# Integration Guide — Release 5.1

Base commit required:

`3e7d9a8ee28f34743ade96de5170ee8686a8c3db`

Run the installer from the extracted release folder. Then execute:

```bash
PYTHONPATH=. pytest -q tests/test_release_5_1_comparative_ranking_engine.py
PYTHONPATH=. pytest -q
```

The official uploaded-candidate score remains stored in `CandidateAnalysisState.match_score`. Comparative dimensions are available in `score_breakdown` under keys prefixed with `comparative_`.
