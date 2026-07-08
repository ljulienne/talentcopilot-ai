# 20 — Document Intelligence Foundation

## Purpose

Document Intelligence converts documents into structured, validated business data.

It is the first real-data entry point of TalentCopilot.

## Pipeline

```text
Document
    ↓
Document Loader
    ↓
Text Cleaner
    ↓
Language Detection
    ↓
Document Segmentation
    ↓
AI Structured Extraction
    ↓
Validation
    ↓
Decision Core ready data
```

## Scope of Package B

This package provides the foundation:

- PDF/DOCX/TXT loader;
- text cleaning;
- language detection;
- CV section segmentation;
- structured candidate extraction through AI Platform Core;
- Streamlit diagnostic page.

## Design rules

1. Document Intelligence does not produce hiring recommendations.
2. LLM output must be structured.
3. Document extraction must remain separate from Decision Core.
4. Future OCR should only run when the document has no extractable text.
