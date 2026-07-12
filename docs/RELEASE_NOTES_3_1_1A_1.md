# Release 3.1.1A.1 — Candidate Identity Extraction

## Problem

A real uploaded resume for Vincent Blakoe was identified as
"Credit Suisse", one of the client organizations mentioned in the CV.

## Resolution

Candidate identity is now resolved deterministically using:

1. personal email address;
2. LinkedIn profile;
3. resume header;
4. uploaded filename;
5. previous pipeline extraction as a final fallback.

Employer and client organization names are explicitly rejected as
candidate identities.

## Interoperability

The corrected identity is written into the official RecruitmentSession
before Candidate Intelligence, Comparison, Interview Intelligence,
Reports or any other downstream module consumes the candidate.
