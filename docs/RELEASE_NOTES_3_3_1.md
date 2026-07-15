# TalentCopilot-AI — Hotfix 3.3.1

## Official Score Cache Invalidation

The real upload pipeline already produces and persists the canonical fit
scores. However, Streamlit could restore an analysis created earlier in the
same browser session when the same documents were uploaded again.

The analysis request key now includes:

`official-fit-session-v3.3.1`

A cached session is restored only when its metadata declares the same score
contract. Older sessions are ignored and the uploaded documents are analysed
again.

No scoring formula is changed by this hotfix.
