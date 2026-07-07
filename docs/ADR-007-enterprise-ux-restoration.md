# ADR-007 — Enterprise UX Restoration

## Status

Accepted

## Context

Temporary fallback UI pages were introduced to stabilize Streamlit imports. They solved deployment errors but made many pages look identical.

## Decision

Create differentiated enterprise-style page templates that remain stable, dependency-light and compatible with the existing app navigation.

## Consequences

Positive:

- pages are visually distinct;
- app feels more product-ready;
- future AI engines can plug into clear UI zones.

Trade-offs:

- this is still not the final polished UI;
- deep data integration remains iterative.
