# Release 7.0.1 — Deterministic Recruitment Scoring

## Objective
Guarantee that identical job and CV documents analysed by the same engine version produce exactly the same official scores and ranks.

## Changes
- Adds a canonical, order-independent scoring fingerprint.
- Starts the isolated scoring worker with a fixed `PYTHONHASHSEED=0`.
- Canonically orders candidate inputs before scoring.
- Makes transferable ontology aliases deterministic.
- Makes real-upload session IDs deterministic for identical inputs.
- Versions the score/session/cache contract and automatically invalidates older cached sessions.
- Adds multi-process repeatability tests across different hash seeds and upload orders.

## Non-goals
This release does not tune benchmark-specific scores and contains no candidate-specific or HRIS-specific ranking rule.
