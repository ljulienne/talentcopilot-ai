# Release 6.1B.1 — Evidence Profile Foundation

Source snapshot: `ab3d056be89d5d9d3e3b8b65e366fe364116a976`.

This release introduces canonical, evidence-grounded candidate and mission profiles. It does not alter Mission Fit, the calibrated official score, or ranking order.

## Added
- `EvidenceItem` with stable ID, excerpt, source, category and confidence.
- `CandidateEvidenceProfile` and deterministic builder.
- `MissionEvidenceProfile` and deterministic builder.
- Pipeline metadata contract for downstream Career, Recruiter, Interview and Decision Intelligence.
- Regression tests protecting the single-source-of-truth score and rank contract.
