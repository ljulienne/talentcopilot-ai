# TalentCopilot Next — Release 0.1B

## Product outcome

Release 0.1B turns Organization Intelligence from a static concept into the first explainable diagnostic engine. The release remains intentionally narrow: it analyzes collaboration metadata, highlights weak cross-team links and hidden connectors, and recommends actions.

## Included

- First real Organization Intelligence service and models.
- CSV upload and demonstration dataset.
- Explainable department and connector signals.
- Privacy-by-design boundaries in the UI.
- Runtime-compatible navigation (`label` and `icon`).
- Product-shell hardening and focused tests.

## Not included yet

- Email or chat-content ingestion.
- Employee surveillance or emotion inference.
- Causal claims about performance.
- Persistent employee records.
- Full graph visualization or SIRH connectors.

## Required CSV columns

`source_person, source_department, target_person, target_department, interactions`

## Validation

Run:

```bash
PYTHONPATH=. TALENTCOPILOT_USE_LLM_EXTRACTION=mock pytest -q
```
