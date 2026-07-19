from __future__ import annotations

# Compact deterministic ontology. It deliberately favours explainability and
# stable behaviour over opaque embeddings. New domains can be added without
# changing the scoring engine.
CONCEPTS = {
    "industry_textile_apparel": ["textile", "apparel", "garment", "fashion", "fabric", "clothing"],
    "industry_software": ["software", "saas", "cloud", "devops", "engineering", "microservices"],
    "industry_retail": ["retail", "store operations", "merchandising"],
    "function_sales": ["sales", "commercial", "business development", "account management", "key account"],
    "function_operations": ["operations", "operational excellence", "supply chain"],
    "function_engineering": ["software engineer", "engineering manager", "developer", "devops"],
    "leadership_regional": ["regional", "country manager", "director", "head of", "apac", "asia pacific"],
    "leadership_people": ["managed a team", "managed teams", "team of", "people manager", "direct reports", "led a team"],
    "commercial_b2b": ["b2b", "business-to-business", "enterprise sales", "strategic accounts", "key accounts"],
    "commercial_pnl": ["p&l", "profit and loss", "revenue", "budget", "forecast", "commercial performance"],
    "geography_apac": ["apac", "asia pacific", "southeast asia", "south east asia", "asean", "asia"],
    "tool_sap": ["sap"],
    "tool_salesforce": ["salesforce", "crm"],
    "tool_power_bi": ["power bi", "powerbi"],
    "skill_negotiation": ["negotiation", "negotiated", "contract negotiation"],
    "skill_pricing": ["pricing", "price strategy"],
    "skill_forecasting": ["forecasting", "forecast"],
    "language_english": ["english"],
    "language_mandarin": ["mandarin", "chinese"],
    "education_mba": ["mba", "master of business administration"],
}

LABELS = {
    "industry_textile_apparel": "Textile / apparel industry",
    "industry_software": "Software / cloud industry",
    "industry_retail": "Retail industry",
    "function_sales": "Sales and commercial leadership",
    "function_operations": "Operations leadership",
    "function_engineering": "Software engineering",
    "leadership_regional": "Regional leadership",
    "leadership_people": "People leadership",
    "commercial_b2b": "B2B commercial scope",
    "commercial_pnl": "P&L, revenue and forecasting",
    "geography_apac": "APAC market experience",
    "tool_sap": "SAP",
    "tool_salesforce": "Salesforce / CRM",
    "tool_power_bi": "Power BI",
    "skill_negotiation": "Negotiation",
    "skill_pricing": "Pricing",
    "skill_forecasting": "Forecasting",
    "language_english": "English",
    "language_mandarin": "Mandarin",
    "education_mba": "MBA",
}

DIMENSION_WEIGHTS = {
    "industry": 0.20,
    "function": 0.20,
    "leadership": 0.16,
    "experience": 0.14,
    "business_scope": 0.12,
    "tools": 0.08,
    "geography": 0.06,
    "education_languages": 0.04,
}
