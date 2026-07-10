# TalentCopilot Next — Release 0.4.1

## Organization Graph Foundation

This release introduces the first reusable organizational graph in TalentCopilot.

### Capabilities

- Employee nodes built from HR exports.
- Manager, shared-skill and backup relationships.
- Explainable relationship evidence.
- Individual connectivity metrics.
- Cross-department connectivity metrics.
- Detection of isolated departments and connector dependency.
- Common `OrganizationInsight` output.
- CSV export of inferred graph relationships.

### Design choice

The graph foundation uses no new third-party graph dependency. It is intentionally lightweight for Google Colab and can later be replaced or extended with NetworkX or a graph database without changing the diagnostic contract.


## Corrective packaging

This cumulative package embeds the Core Intelligence dependency required by the graph engine.
