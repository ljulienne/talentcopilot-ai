# Integration Guide — Release 7.8.2

1. Install the package on `main` at commit `060ad575b0d5bb0c5f49a3da90d1baf31e0f5359`.
2. Confirm `.talentcopilot_release` reports `7.8.2-candidate-insight-grounding`.
3. Reopen the same recruitment mission used to report the issue.
4. Open **Dashboard Perspective**.
5. Confirm each candidate card derives **Strongest area** from that candidate's evidence, not from role-requirement order.
6. Confirm **Primary risk** uses the candidate's highest-priority grounded risk and is not a duplicated generic fallback.
7. Download the candidate dashboard PDF and verify it shows the same strongest area and primary risk as the cards.
8. Confirm official scores and ranks remain unchanged.
9. Run the targeted Release 7.8.2 tests and the complete test suite before pushing.
