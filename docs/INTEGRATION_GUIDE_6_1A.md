# Integration Guide — Release 6.1A

The real ranking pipeline invokes `RecruiterIntelligenceEngine` after calibrated scoring. The assessment is serialized in the decision profile metadata under `recruiter_intelligence`.

Key metadata:
- `recruiter_intelligence_engine`
- `recruiter_intelligence`
- `recruiter_strategic_fit`
- `recruiter_confidence`
- `recruiter_summary`
- `candidate_dna`
- `recruiter_decisive_strengths`
- `recruiter_material_gaps`
- `recruiter_interview_focus`

This release intentionally has no score or ranking authority. UI and comparative executive reasoning are reserved for Releases 6.1B and 6.1C.
