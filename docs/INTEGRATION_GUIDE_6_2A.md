# Integration Guide — Release 6.2A

Use `RecruitmentSourceOfTruthService().get(session)` to read the canonical recruitment snapshot.

Use `ordered_analyses(session)` for UI/workspace services. Do not sort or recalculate official scores in downstream pages.

The snapshot is persisted under `session.metadata["recruitment_source_of_truth"]` and cached by session ID. Any mutation to official score or rank after freezing raises `SourceOfTruthViolation`.
