# TalentCopilot-AI — Release 3.4

## Isolated Canonical Scoring

Real-upload scoring is now executed in a clean Python subprocess,
outside Streamlit rerun state and process-level mutable state.

The subprocess receives the exact text documents already extracted by
UploadTextReaderService and returns the official RecruitmentSession.

Public score contract:

- Official Match = fit score
- AI Confidence = confidence score
- ranking score remains internal

The release cannot be committed by the installation procedure unless
the real calibration files produce exactly:

- Louis Julienne: 86
- Vincent Blakoe: 66
- Loretta Danielson: 30
- Zelma O'Reilly: 25
