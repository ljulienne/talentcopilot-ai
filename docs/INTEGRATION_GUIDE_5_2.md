# Integration Guide — Release 5.2

The `RealRankingPipeline` now invokes `CalibratedMissionScoringEngine` after Mission Fit v2 and Comparative Ranking.

Canonical fields stored in profile metadata:

- `calibrated_scoring_engine`
- `calibrated_score`
- `calibrated_confidence`
- `calibrated_band`
- `calibrated_breakdown`
- `calibrated_limiting_factors`

The official `profile.fit_score` and upload-session `match_score` are the calibrated values. Raw Mission Fit dimensions remain available for explainability and audit.
