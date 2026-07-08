# ADR-013 — Progressive workspace migration

## Status

Accepted

## Context

Release 1.1 workspaces are already functional.

Replacing them all at once with Decision Core v2 would create migration risk.

## Decision

Use a bridge service to progressively connect current session data to Decision Core outputs.

## Consequences

- Existing UI remains stable.
- New Decision Core can be tested with real session-like data.
- Migration can happen workspace by workspace.
