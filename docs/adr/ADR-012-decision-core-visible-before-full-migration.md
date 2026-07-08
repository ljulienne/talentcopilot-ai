# ADR-012 — Decision Core visible before full workspace migration

## Status

Accepted

## Context

Existing workspaces were built before Decision Intelligence Core v2.

Migrating every workspace at once would create unnecessary risk.

## Decision

Expose Decision Core v2 first through a dedicated page.

## Consequences

- The new engine can be tested and demonstrated immediately.
- Existing workspaces remain stable.
- Progressive migration becomes safer.
