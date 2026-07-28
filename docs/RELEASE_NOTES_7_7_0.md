# TalentCopilot-AI Release 7.7.0

## Domain-Agnostic Requirement Intelligence

Release 7.7.0 replaces the HRIS-specific requirement definitions introduced in 7.6.0 with a dynamic, domain-agnostic extraction architecture.

### Main changes

- Extracts exact software, platforms, standards, methodologies, certifications and role capabilities from the wording of each offer at runtime.
- Does not require a product to be pre-registered in a role-specific catalogue.
- Uses a deterministic offline engine as the safe baseline.
- Can optionally enrich the grounded deterministic result with an OpenAI structured extraction when `OPENAI_API_KEY` is configured.
- Rejects ungrounded enrichment entries whose source excerpt or distinctive terms cannot be found in the offer.
- Classifies requirements into reusable families such as software engineering, databases, cloud/DevOps, finance systems, CRM/sales, supply chain, marketing technology, HRIS, business intelligence, AI and methods/frameworks.
- Distinguishes direct, ambiguous, related/transferable and absent CV evidence.
- Generates interview questions from requirement kind, family and evidence status rather than from a role-specific question list.
- Keeps eligibility conditions such as degree, years and languages outside the competency radar.
- Preserves a maximum of nine decision-relevant radar axes.
- Regenerates older 7.6 embedded catalogues from the raw offer so the previous HRIS assumptions do not leak into other roles.
- Does not modify official fit scores, official ranks or canonical recommendations.

### Multi-domain benchmark

The release includes deterministic regression scenarios for:

- HRIS Manager
- Backend Software Engineer
- Group Financial Controller
- Senior Sales Manager APAC
- Supply Chain Project Manager
- Digital Marketing Manager

The benchmark verifies exact requirement extraction, absence of HRIS leakage, contextual candidate evidence, transferable-technology detection, eligibility separation and generic interview probing.

### HRIS non-regression

The supplied HRIS test case remains protected. Its first three decision axes remain:

1. SAP SuccessFactors & Core HR
2. Power BI & HR Reporting
3. AI Solutions for HR

Power BI remains direct evidence for Louis Julienne, while SuccessFactors and applied AI remain targeted transferability or gap probes.

### Quality boundary

The deterministic engine is designed to work offline and on previously unseen terms. Optional model enrichment improves classification and phrasing for complex or unusual offers, but every enriched result is source-grounded and the deterministic result remains available as a fallback.
