# Integration Guide — Release 7.0.1

1. Install the release package on the latest clean `main`.
2. Run the targeted deterministic tests.
3. Run the full pytest suite.
4. Upload the same job and CV set at least three times, including a different CV selection order.
5. Confirm exact equality of Official Match, Mission Fit rank and Decision Priority for every candidate.
6. Commit and push only after all checks pass.
