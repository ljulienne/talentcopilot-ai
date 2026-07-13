# Release 3.2.1A.2.2 — Cloud Consistency & Performance

## Fixes

- Every real-upload RecruitmentSession records explicit analysis provenance.
- Real-upload sessions produced by older pipelines are invalidated automatically.
- The upload workflow uses a Streamlit form to avoid reruns while selecting files.
- Identical documents are restored from a browser-session-local analysis cache.
- Candidate CV data is not stored in a global cross-user Streamlit cache.
- Extraction, ranking/session and total execution times are recorded.
- The official upload pipeline is explicitly identified as `real-upload-ranking`.

## Matching

No score, weighting, ranking or matching algorithm is changed.
