# 19 — AI Platform Core

## Purpose

The AI Platform Core is the reusable AI infrastructure layer of TalentCopilot.

It is independent from recruitment business logic.

## Responsibilities

- route LLM requests;
- manage prompt versions;
- enforce structured outputs;
- track cost and latency;
- cache repeated requests;
- log observability events;
- register available models.

## Design rules

1. AI Platform Core does not make hiring decisions.
2. LLM outputs must be structured.
3. Every AI request should be observable.
4. Prompt versions must be explicit.
5. Cost should be tracked from the beginning.
6. Business scoring remains inside Decision Intelligence Core.

## Target data flow

```text
Feature Service
        ↓
Prompt Manager
        ↓
LLM Router
        ↓
Structured Output
        ↓
Validation
        ↓
Business Engine
```
