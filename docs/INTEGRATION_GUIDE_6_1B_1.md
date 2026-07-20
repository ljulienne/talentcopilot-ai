# Integration Guide — Release 6.1B.1

The canonical profiles live in `talentcopilot.evidence_profiles`. Build them once from the already extracted candidate and role data, then pass or serialize them for downstream reasoning.

`RealRankingPipeline` now publishes `candidate_evidence_profile`, `mission_evidence_profile`, their builder versions, and `evidence_profile_contract` in profile metadata. These fields are explanatory inputs only. They must never overwrite `fit_score`, `rank`, candidate identity, or calibrated scoring metadata.

Future 6.1B.2 Career Intelligence must consume these profiles rather than re-extracting CV and job text independently.
