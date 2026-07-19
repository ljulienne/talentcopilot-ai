"""Universal deterministic concept ontology for Mission Fit.

Release 6.0B.3.1 extends the original sales benchmark vocabulary to multiple
job families while preserving the existing concept keys and eight score
dimensions.
"""

DIMENSION_WEIGHTS = {
    "industry": 0.15,
    "function": 0.20,
    "leadership": 0.12,
    "experience": 0.18,
    "business_scope": 0.12,
    "tools": 0.10,
    "geography": 0.06,
    "education_languages": 0.07,
}

CONCEPTS = {
    # Industries / domains
    "industry_textile_apparel": (
        "textile", "apparel", "garment", "fabric", "fashion manufacturing",
    ),
    "industry_software": (
        "software", "saas", "cloud", "technology company", "tech company",
    ),
    "industry_retail": ("retail", "store operations", "e-commerce"),
    "industry_hr_technology": (
        "hris", "sirh", "hr systems", "human resources information system",
        "people systems", "hr technology", "hr tech",
    ),
    "industry_financial_services": (
        "banking", "financial services", "insurance", "fintech",
    ),
    "industry_manufacturing": (
        "manufacturing", "industrial", "factory", "production plant",
    ),
    "industry_logistics": (
        "logistics", "supply chain", "transportation", "warehouse",
    ),

    # Functions
    "function_sales": (
        "sales manager", "sales director", "commercial manager",
        "commercial director", "business development", "key account",
        "account executive", "b2b sales",
    ),
    "function_operations": (
        "operations manager", "operations director", "operational excellence",
        "store operations",
    ),
    "function_engineering": (
        "software engineer", "engineering manager", "engineering director",
        "developer", "devops", "cloud architect",
    ),
    "function_hris": (
        "hris manager", "hris project manager", "hr systems manager",
        "sirh", "responsable sirh", "chef de projet sirh",
        "hr technology", "people systems",
    ),
    "function_human_resources": (
        "human resources", "hr manager", "hr business partner",
        "talent management", "people operations",
    ),
    "function_finance": (
        "finance manager", "financial controller", "accounting manager",
        "fp&a", "financial planning", "chief financial officer", "cfo",
    ),
    "function_supply_chain": (
        "supply chain manager", "logistics manager", "procurement manager",
        "planning manager", "warehouse manager",
    ),
    "function_data": (
        "data analyst", "data scientist", "business intelligence",
        "analytics manager", "people analytics",
    ),
    "function_marketing": (
        "marketing manager", "marketing director", "brand manager",
        "digital marketing",
    ),

    # Leadership
    "leadership_regional": (
        "regional", "apac", "asia pacific", "emea", "global",
        "multi-country", "multiple countries", "international scope",
    ),
    "leadership_people": (
        "managed a team", "managed teams", "led a team", "led teams",
        "team leadership", "people management", "encadrement",
        "management d'équipe", "manager of managers",
    ),

    # Business scope / transferable capabilities
    "commercial_b2b": ("b2b", "business-to-business", "key accounts"),
    "commercial_pnl": ("p&l", "profit and loss", "revenue ownership", "budget ownership"),
    "skill_negotiation": ("negotiation", "négociation", "contract negotiation"),
    "skill_pricing": ("pricing", "tarification"),
    "skill_forecasting": ("forecasting", "forecast", "prévisions"),
    "skill_project_management": (
        "project management", "program management", "gestion de projet",
        "pilotage de projet", "pmo",
    ),
    "skill_change_management": (
        "change management", "conduite du changement",
        "accompagnement du changement", "user adoption",
    ),
    "skill_stakeholder_management": (
        "stakeholder management", "stakeholders", "parties prenantes",
        "business partnering", "relations métiers",
    ),
    "skill_process_design": (
        "process design", "process improvement", "business process",
        "process optimization", "amélioration des processus",
    ),
    "skill_reporting": (
        "reporting", "dashboard", "kpi", "business intelligence",
        "business objects", "power bi",
    ),
    "skill_integration": (
        "api", "integration", "intégration", "interface", "interfaces",
        "web service", "system integration",
    ),
    "skill_payroll": ("payroll", "paie", "gestion de la paie"),
    "skill_time_management": (
        "time management", "workforce management", "gestion des temps",
        "gta", "octime",
    ),

    # Tools
    "tool_sap": ("sap",),
    "tool_salesforce": ("salesforce",),
    "tool_power_bi": ("power bi",),
    "tool_workday": ("workday",),
    "tool_successfactors": ("successfactors", "sap successfactors", "sap sf"),
    "tool_oracle_hcm": ("oracle hcm", "oracle cloud hcm"),
    "tool_talentsoft": ("talentsoft", "cegid talentsoft"),
    "tool_excel": ("excel",),
    "tool_sql": ("sql",),
    "tool_python": ("python",),

    # Geography / languages / education
    "geography_apac": ("apac", "asia pacific", "southeast asia", "north asia", "oceania"),
    "geography_emea": ("emea", "europe middle east africa"),
    "geography_global": ("global", "worldwide", "international"),
    "language_english": ("english", "anglais"),
    "language_mandarin": ("mandarin", "chinese", "chinois"),
    "language_french": ("french", "français", "francais"),
    "education_mba": ("mba", "master of business administration"),
    "education_degree": ("bachelor", "master degree", "university degree", "licence", "diplôme"),
}

LABELS = {
    key: key.replace("_", " ").title()
    for key in CONCEPTS
}

LABELS.update({
    "industry_hr_technology": "HR technology / HRIS domain",
    "function_hris": "HRIS / HR systems function",
    "skill_project_management": "Project management",
    "skill_change_management": "Change management",
    "skill_stakeholder_management": "Stakeholder management",
    "skill_reporting": "Reporting and analytics",
    "skill_integration": "Systems integration / APIs",
    "skill_payroll": "Payroll",
    "skill_time_management": "Time and attendance",
    "tool_successfactors": "SAP SuccessFactors",
    "tool_oracle_hcm": "Oracle HCM",
})
