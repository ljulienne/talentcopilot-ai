# 26 — Real Extraction Upgrade

## Purpose

Real Extraction Upgrade improves the quality of real CV and job description parsing.

## Why

The previous extraction layer was intentionally minimal and mock-based. It could read files but did not understand enough real-world vocabulary.

## Improvements

- skill ontology;
- synonyms;
- French and English HR vocabulary;
- HRIS/SIRH vocabulary;
- payroll and time management vocabulary;
- experience detection;
- language detection;
- certifications;
- quantified achievements;
- richer candidate dictionaries for Decision Core.

## Design rules

1. Extraction remains separate from Decision Core.
2. The Decision Core still owns scoring.
3. Normalization should make matching less keyword-fragile.
4. Missing LLM integration remains explicit.
