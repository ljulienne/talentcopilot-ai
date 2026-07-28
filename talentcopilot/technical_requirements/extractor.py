from __future__ import annotations

import json
import os
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable

from talentcopilot.technical_requirements.models import TechnicalRequirement


@dataclass
class _RequirementDraft:
    name: str
    category: str
    family: str
    kind: str
    importance: str
    level: float
    source: str
    aliases: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    priority: str = "Validate"
    method: str = "deterministic"
    order: int = 0
    specificity: int = 0


class DomainAgnosticRequirementExtractor:
    """Extract role requirements without relying on a role-specific product list.

    The deterministic path derives exact tools, platforms, methodologies and
    capabilities from the wording of the offer. Optional LLM enrichment can add
    context, but all results are grounded back to source excerpts and merged with
    deterministic findings so an unavailable model never blocks the workflow.
    """

    MAX_REQUIREMENTS = 12

    _SECTION_HEADINGS = {
        "requirements", "required skills", "skills", "qualifications", "profile",
        "responsibilities", "main responsibilities", "job responsibilities",
        "missions", "mission", "what you will do", "what you bring", "experience",
        "competencies", "key competencies", "preferred qualifications",
    }

    _STOP_TERMS = {
        "about", "about us", "additional information", "apply", "benefits", "company",
        "description", "excellent", "full time", "higher education", "job", "location",
        "main responsibilities", "minimum", "position", "profile", "responsibilities",
        "role", "strong", "the role", "what you bring", "what you will do",
        "work experience", "professional experience", "education", "skills",
        "english", "french", "german", "spanish", "mandarin", "communication",
    }

    _GENERIC_WORDS = {
        "ability", "activities", "business", "candidate", "collaboration", "communication",
        "company", "environment", "experience", "expertise", "group", "knowledge",
        "management", "manager", "process", "project", "projects", "responsibility",
        "responsibilities", "role", "skills", "solution", "solutions", "support", "system",
        "systems", "team", "teams", "tool", "tools", "work",
    }

    # Cross-domain capabilities. These are semantic delivery patterns, not a
    # catalogue of products or professions.
    _CAPABILITY_RULES = (
        (
            "Project Leadership & Delivery", "Leadership & Delivery", "Programme Delivery",
            "delivery_capability", ("project management", "program management", "programme management",
            "lead complex projects", "project leadership", "project planning", "project delivery",
            "manage projects", "coordinate projects"),
        ),
        (
            "Interfaces & Technical Delivery", "Technology & Delivery", "Integration & Testing",
            "technical_delivery", ("third party systems", "third-party systems", "system interfaces",
            "interfaces", "integration", "api", "acceptance testing", "functional testing",
            "technical testing", "uat", "sit", "data flows"),
        ),
        (
            "Data Quality & Governance", "Data & Analytics", "Data Governance",
            "data_governance", ("data quality", "data cleaning", "data reliability", "data accuracy",
            "data integrity", "data governance", "master data", "data controls"),
        ),
        (
            "Change Management & Adoption", "Transformation", "Change & Adoption",
            "functional_capability", ("change management", "user adoption", "adoption", "training plan",
            "communication plan", "upskilling", "post deployment support", "post-deployment support",
            "conduite du changement"),
        ),
        (
            "Vendor & Stakeholder Management", "Leadership & Delivery", "Stakeholder Governance",
            "delivery_capability", ("vendor management", "supplier management", "solution providers",
            "external providers", "integrators", "stakeholder management", "steering committee",
            "project committee", "client management"),
        ),
        (
            "Team Leadership & International Delivery", "Leadership & Delivery", "People Leadership",
            "leadership_capability", ("team leadership", "team management", "people management",
            "manage a team", "managing a team", "supporting collaborators", "international environment",
            "international projects", "multi country", "multi-country", "global environment"),
        ),
        (
            "Software Architecture & Engineering", "Technology & Engineering", "Software Engineering",
            "technical_capability", ("software architecture", "backend engineering", "backend development",
            "software development", "microservices", "distributed systems", "application architecture"),
        ),
        (
            "Quality & Automated Testing", "Technology & Engineering", "Quality Engineering",
            "technical_capability", ("automated testing", "unit testing", "integration testing",
            "test automation", "quality assurance", "code quality", "testing strategy"),
        ),
        (
            "Cloud & DevOps Delivery", "Technology & Engineering", "Cloud & DevOps",
            "technical_capability", ("cloud infrastructure", "devops", "ci cd", "continuous integration",
            "continuous delivery", "containerization", "containers", "infrastructure as code"),
        ),
        (
            "Financial Reporting & Consolidation", "Finance", "Financial Reporting",
            "functional_capability", ("financial reporting", "group consolidation", "consolidation",
            "monthly closing", "month end close", "month-end close", "statutory reporting"),
        ),
        (
            "Planning, Budgeting & Forecasting", "Finance & Planning", "Planning & Forecasting",
            "functional_capability", ("budgeting", "financial planning", "budget control",
            "budget management", "variance analysis", "business planning"),
        ),
        (
            "Internal Controls & Compliance", "Risk & Compliance", "Controls & Compliance",
            "risk_capability", ("internal controls", "internal control", "compliance", "audit controls",
            "risk controls", "regulatory compliance", "sox"),
        ),
        (
            "Enterprise Sales & Account Growth", "Commercial", "Enterprise Sales",
            "commercial_capability", ("enterprise sales", "complex sales", "consultative sales",
            "key accounts", "strategic accounts", "account growth", "business development"),
        ),
        (
            "Pipeline & Revenue Forecasting", "Commercial", "Sales Operations",
            "commercial_capability", ("sales pipeline", "pipeline management", "revenue forecast",
            "sales forecasting", "forecast accuracy", "quota attainment", "sales operations"),
        ),
        (
            "Supply Planning & S&OP", "Supply Chain", "Planning & S&OP",
            "operational_capability", ("sales and operations planning", "s and op", "s&op",
            "supply planning", "demand planning", "production planning"),
        ),
        (
            "Inventory & Logistics Optimisation", "Supply Chain", "Logistics & Inventory",
            "operational_capability", ("inventory optimization", "inventory optimisation", "inventory management",
            "logistics", "warehousing", "distribution", "transportation management"),
        ),
        (
            "Supplier & Procurement Management", "Supply Chain", "Procurement & Suppliers",
            "operational_capability", ("supplier management", "procurement", "strategic sourcing",
            "purchasing", "supplier performance", "vendor negotiation"),
        ),
        (
            "Digital Marketing & Acquisition", "Marketing", "Growth Marketing",
            "marketing_capability", ("digital marketing", "customer acquisition", "paid campaigns",
            "paid media", "campaign management", "growth marketing", "conversion optimization",
            "conversion optimisation"),
        ),
        (
            "SEO & Web Analytics", "Marketing", "Search & Analytics",
            "marketing_capability", ("search engine optimization", "search engine optimisation", "seo",
            "web analytics", "organic search", "keyword research", "traffic analysis"),
        ),
        (
            "Operational Excellence & Continuous Improvement", "Operations", "Operational Excellence",
            "operational_capability", ("continuous improvement", "operational excellence", "lean management",
            "process improvement", "process optimisation", "process optimization", "root cause analysis"),
        ),
        (
            "Quality, Safety & Reliability", "Operations", "Quality & Reliability",
            "risk_capability", ("quality management", "quality assurance", "health and safety", "safety management",
            "system reliability", "asset reliability", "preventive maintenance", "corrective maintenance"),
        ),
    )

    _KIND_SUFFIXES = (
        "management", "planning", "forecasting", "reporting", "analytics", "analysis",
        "architecture", "engineering", "development", "testing", "governance", "compliance",
        "consolidation", "recruitment", "marketing", "sales", "logistics", "procurement",
        "maintenance", "quality", "security", "leadership", "negotiation", "design",
    )

    _CUE_PATTERNS = (
        r"(?:experience|expertise|knowledge|proficiency|mastery|familiarity|skills?)\s+(?:in|with|of|on)\s+([^.;\n]+)",
        r"(?:experienced|proficient|skilled|certified)\s+(?:in|with)\s+([^.;\n]+)",
        r"(?:must have|required|essential|mandatory|preferred|nice to have)\s*[:\-]?\s*([^.;\n]+)",
        r"(?:maitrise|maîtrise|connaissance|experience|expérience|expertise)\s+(?:de|des|du|en|avec)\s+([^.;\n]+)",
    )

    _ACTION_MARKERS = (
        "implement", "implemented", "design", "designed", "develop", "developed", "build", "built",
        "configure", "configured", "deploy", "deployed", "lead", "led", "manage", "managed",
        "deliver", "delivered", "create", "created", "launch", "launched", "own", "owned",
        "test", "tested", "validate", "validated", "audit", "audited", "apply", "applied", "optimise", "optimize",
        "mis en place", "déploy", "conçu", "pilot", "lancé", "géré", "dirigé",
    )

    _IMPORTANCE_CRITICAL = (
        "must", "required", "essential", "mandatory", "excellent knowledge", "strong knowledge",
        "proficiency", "proficient", "expertise", "mastery", "maîtrise", "indispensable",
    )
    _IMPORTANCE_PREFERRED = ("preferred", "nice to have", "desirable", "a plus", "souhaité")

    _FAMILY_RULES = (
        ("HRIS Platforms", "Technology & HRIS", ("hris", "human resources", "core hr", "payroll", "talent management", "people system")),
        ("Business Intelligence", "Data & Analytics", ("report", "dashboard", "business intelligence", "analytics", "kpi", "visualization", "visualisation")),
        ("Data & Databases", "Data & Analytics", ("database", "sql", "data warehouse", "data lake", "etl", "data model")),
        ("Applied Artificial Intelligence", "Innovation & Data", ("artificial intelligence", "machine learning", "generative ai", "data science", "predictive", "nlp", "intelligence artificielle")),
        ("Software Engineering", "Technology & Engineering", ("software", "backend", "frontend", "api", "microservice", "application development", "programming")),
        ("Cloud & DevOps", "Technology & Engineering", ("cloud", "devops", "container", "ci cd", "deployment pipeline", "infrastructure")),
        ("Cybersecurity", "Risk & Compliance", ("cybersecurity", "information security", "security", "iam", "vulnerability", "threat")),
        ("Finance Systems", "Finance", ("finance", "financial", "accounting", "consolidation", "general ledger", "erp", "controlling")),
        ("CRM & Sales Platforms", "Commercial", ("crm", "sales", "pipeline", "account management", "customer relationship")),
        ("Supply Chain Systems", "Supply Chain", ("supply chain", "logistics", "inventory", "warehouse", "procurement", "manufacturing")),
        ("Marketing Technology", "Marketing", ("marketing", "campaign", "seo", "web analytics", "acquisition", "advertising")),
        ("Quality & Operations", "Operations", ("quality", "lean", "six sigma", "maintenance", "operations", "safety")),
        ("Project & Delivery Methods", "Leadership & Delivery", ("project", "programme", "program", "agile", "scrum", "waterfall", "delivery")),
    )

    _ADJACENT_FAMILIES = {
        "Applied Artificial Intelligence": ("Data & Databases", "Business Intelligence", "Software Engineering"),
        "Business Intelligence": ("Data & Databases",),
        "HRIS Platforms": ("Business Intelligence", "Data & Databases", "Project & Delivery Methods"),
        "Software Engineering": ("Data & Databases", "Cloud & DevOps"),
        "Finance Systems": ("Business Intelligence", "Data & Databases"),
        "CRM & Sales Platforms": ("Business Intelligence",),
        "Supply Chain Systems": ("Business Intelligence", "Data & Databases"),
        "Marketing Technology": ("Business Intelligence", "Data & Databases"),
    }

    def extract(
        self,
        text: str,
        *,
        role_title: str = "Recruitment",
        fallback: Iterable[object] = (),
        limit: int = 9,
    ) -> tuple[list[TechnicalRequirement], str]:
        deterministic = self._deterministic(text, role_title=role_title, fallback=fallback)
        method = "deterministic-domain-agnostic"

        llm = self._llm_requirements(text, role_title=role_title)
        if llm:
            drafts = self._merge(llm, deterministic)
            method = "hybrid-domain-agnostic"
        else:
            drafts = deterministic

        selected = self._select(drafts, limit=limit)
        return [self._to_requirement(item) for item in selected], method

    def eligibility(self, text: str) -> tuple[str, ...]:
        clean = " ".join(str(text or "").split())
        plain = self._plain(clean)
        checks: list[str] = []

        years = re.findall(r"(?:minimum(?:\s+of)?|at least|minimum de)?\s*(\d{1,2})\+?\s*(?:years?\b|ans?\b)", plain)
        if years:
            checks.append(f"Minimum experience: {max(int(value) for value in years)} years")

        degree_patterns = (
            ("Doctorate degree", r"\b(?:phd|doctorate|doctoral)\b"),
            ("Master's degree", r"\b(?:master(?:'s)?|mba|msc|bac\s*\+?\s*5)\b"),
            ("Bachelor's degree", r"\b(?:bachelor(?:'s)?|bsc|ba degree|bac\s*\+?\s*3)\b"),
        )
        for label, pattern in degree_patterns:
            if re.search(pattern, plain):
                checks.append(label)
                break

        language_pattern = re.compile(
            r"\b(?:fluent|professional|bilingual|native|courant|bilingue|maitrise|maîtrise)\s+(?:in\s+|en\s+)?([a-z]{4,18})\b",
            re.I,
        )
        for match in language_pattern.finditer(clean):
            language = match.group(1).title()
            label = f"Language: {language}"
            if label not in checks:
                checks.append(label)

        certifications = re.findall(
            r"\b(?:certification|certified|certification in|certifie|certifié)\s+([A-Za-z0-9][A-Za-z0-9 /+.-]{2,45})",
            clean,
            flags=re.I,
        )
        for value in certifications[:3]:
            label = f"Certification: {self._clean_phrase(value)}"
            if label not in checks:
                checks.append(label)

        return tuple(checks)

    def extract_candidate_entities(self, text: str) -> list[tuple[str, str, str]]:
        """Return (entity, family, excerpt) tuples from a CV without a product list."""
        entities: list[tuple[str, str, str]] = []
        heading = ""
        for index, line in enumerate(self._lines(text)):
            if self._looks_like_heading(line):
                heading = line
            context = f"{heading} {line}"
            for term in self._named_terms(line):
                family, _ = self._family(context, term)
                item = (term, family, line[:300])
                if not any(self._plain(existing[0]) == self._plain(term) for existing in entities):
                    entities.append(item)
            for captured in self._cue_terms(line):
                family, _ = self._family(context, captured)
                item = (captured, family, line[:300])
                if not any(self._plain(existing[0]) == self._plain(captured) for existing in entities):
                    entities.append(item)
            if len(entities) >= 60:
                break
        return entities

    def adjacent_families(self, family: str) -> tuple[str, ...]:
        return self._ADJACENT_FAMILIES.get(str(family or ""), ())

    def _deterministic(self, text: str, *, role_title: str, fallback: Iterable[object]) -> list[_RequirementDraft]:
        lines = self._lines(text)
        domain = self._domain_label(role_title, text)
        drafts: list[_RequirementDraft] = []

        for index, line in enumerate(lines):
            plain = self._plain(line)
            if not plain or self._is_noise_line(line):
                continue
            if index == 0 and len(line) <= 90 and not re.search(r"[.!?]$", line):
                continue
            if plain == self._plain(role_title):
                continue

            importance, level = self._importance(line)
            context_terms = self._context_terms(line)

            # Explicit AI phrasing is a generic technology class rather than a
            # product-specific definition.
            if any(phrase in plain for phrase in ("artificial intelligence", "generative ai", "machine learning", "intelligence artificielle")):
                label = "AI Solutions" + (f" for {domain}" if domain else "")
                drafts.append(
                    _RequirementDraft(
                        name=label,
                        category="Innovation & Data",
                        family="Applied Artificial Intelligence",
                        kind="technical_innovation",
                        importance=importance if importance != "Supporting" else "High",
                        level=max(3.0, level),
                        source=line,
                        aliases=self._unique(["Artificial Intelligence", "AI", "Generative AI", "Machine Learning"]),
                        related=["data science", "analytics", "automation", "predictive", "python", "nlp"],
                        components=["Artificial Intelligence"],
                        context=context_terms,
                        priority="Mandatory probe" if importance == "Critical" else "Validate",
                        order=index,
                        specificity=9,
                    )
                )

            named = self._named_terms(line)
            named.extend(self._cue_terms(line))
            named = self._unique(named)
            for term in named:
                if not self._valid_requirement_term(term) or not self._looks_like_named_requirement(term, line):
                    continue
                local_context = line
                for other in named:
                    if self._plain(other) != self._plain(term):
                        local_context = re.sub(re.escape(other), " ", local_context, flags=re.I)
                family, category = self._family(local_context, term)
                if family == "Technical Tools & Platforms":
                    fallback_family, fallback_category = self._family(role_title, term)
                    if fallback_family != "Technical Tools & Platforms":
                        family, category = fallback_family, fallback_category
                kind = self._kind(term, local_context, family)
                name = self._compose_name(term, line, domain, family, global_text=text)
                aliases = self._aliases(term)
                related = self._related_terms(line, term, family)
                drafts.append(
                    _RequirementDraft(
                        name=name,
                        category=category,
                        family=family,
                        kind=kind,
                        importance=importance,
                        level=level,
                        source=line,
                        aliases=aliases,
                        related=related,
                        components=[term],
                        context=context_terms,
                        priority="Mandatory probe" if importance == "Critical" else "Validate",
                        order=index,
                        specificity=(
                            5 if self._plain(term) in {"hris", "crm", "erp", "business intelligence"}
                            else 10 if kind in {"technical_tool", "technical_platform", "certification", "methodology"}
                            else 7
                        ),
                    )
                )

            capability_matched = False
            for name, category, family, kind, patterns in self._CAPABILITY_RULES:
                matched = [pattern for pattern in patterns if self._contains_phrase(plain, pattern)]
                if not matched:
                    continue
                capability_matched = True
                capability_name = self._domain_capability_name(name, domain, plain)
                drafts.append(
                    _RequirementDraft(
                        name=capability_name,
                        category=category,
                        family=family,
                        kind=kind,
                        importance=importance,
                        level=level,
                        source=line,
                        aliases=self._unique(list(patterns) + [capability_name]),
                        related=self._unique(matched + context_terms),
                        components=self._unique(matched[:4]),
                        context=context_terms,
                        priority="Mandatory probe" if importance == "Critical" else "Validate",
                        order=index,
                        specificity=5,
                    )
                )

            if capability_matched:
                continue
            for phrase in self._noun_capabilities(line):
                family, category = self._family(line, phrase)
                drafts.append(
                    _RequirementDraft(
                        name=self._title_phrase(phrase),
                        category=category,
                        family=family,
                        kind="general_capability",
                        importance=importance,
                        level=level,
                        source=line,
                        aliases=[phrase],
                        related=self._related_terms(line, phrase, family),
                        components=[phrase],
                        context=context_terms,
                        priority="Validate",
                        order=index,
                        specificity=4,
                    )
                )

        for offset, raw in enumerate(fallback or (), start=len(lines) + 1):
            if isinstance(raw, dict):
                term = str(raw.get("name") or raw.get("skill") or raw.get("competency") or "").strip()
            else:
                term = str(raw or "").strip()
            if not term or len(term) > 90:
                continue
            family, category = self._family(text, term)
            drafts.append(
                _RequirementDraft(
                    name=term,
                    category=category,
                    family=family,
                    kind="general_capability",
                    importance="High",
                    level=4.0,
                    source="Extracted from the structured role requirements.",
                    aliases=self._aliases(term),
                    related=[],
                    components=[term],
                    context=[],
                    priority="Validate",
                    order=offset,
                    specificity=8,
                )
            )

        return self._dedupe(drafts)

    def _llm_requirements(self, text: str, *, role_title: str) -> list[_RequirementDraft]:
        mode = os.environ.get("TALENTCOPILOT_REQUIREMENT_MODE", "auto").strip().lower()
        if mode in {"deterministic", "offline", "false", "0", "no"}:
            return []
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return []
        try:
            from openai import OpenAI
        except Exception:
            return []

        prompt = f"""
Extract a domain-agnostic catalogue of the most decision-relevant requirements from this job offer.
Do not assume an HR domain. Preserve exact product, software, regulation, methodology, certification and language names.
Separate precise technologies from general capabilities. Do not invent a requirement that is absent from the source.
Return at most 12 requirements. For every requirement provide a verbatim source_excerpt from the offer.
Eligibility conditions such as degree, location, years and languages must not be competency radar axes.

Role title: {role_title}
Job offer:
{text[:12000]}

Return JSON only with this structure:
{{"requirements":[{{"name":"", "category":"", "family":"", "requirement_kind":"technical_tool|technical_platform|technical_innovation|methodology|certification|functional_capability|delivery_capability|leadership_capability|general_capability", "importance":"Critical|High|Supporting", "required_level":0, "source_excerpt":"", "aliases":[], "related_terms":[], "components":[], "context_terms":[], "interview_priority":""}}]}}
""".strip()
        try:
            client = OpenAI(api_key=api_key)
            model = os.environ.get("TALENTCOPILOT_LLM_MODEL", "gpt-5-mini")
            response = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": "You are a precise, domain-agnostic job requirement extraction engine. Output strict JSON."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = getattr(response, "output_text", "") or ""
            payload = json.loads(content)
        except Exception:
            return []

        drafts: list[_RequirementDraft] = []
        source_plain = self._plain(text)
        for index, item in enumerate(payload.get("requirements", [])[: self.MAX_REQUIREMENTS]):
            if not isinstance(item, dict):
                continue
            name = self._clean_phrase(item.get("name"))
            excerpt = self._clean_phrase(item.get("source_excerpt"))
            if not name or not excerpt:
                continue
            # Ground the answer: at least one distinctive name/component token or
            # the excerpt itself must be present in the job text.
            name_tokens = [token for token in self._plain(name).split() if len(token) >= 4]
            if self._plain(excerpt) not in source_plain and not any(token in source_plain for token in name_tokens):
                continue
            try:
                level = float(item.get("required_level") or 4.0)
            except (TypeError, ValueError):
                level = 4.0
            drafts.append(
                _RequirementDraft(
                    name=name,
                    category=self._clean_phrase(item.get("category")) or "Role Capability",
                    family=self._clean_phrase(item.get("family")) or "Role requirement",
                    kind=self._clean_phrase(item.get("requirement_kind")) or "general_capability",
                    importance=self._importance_value(item.get("importance")),
                    level=max(0.0, min(5.0, level)),
                    source=excerpt,
                    aliases=self._list_values(item.get("aliases"), default=[name]),
                    related=self._list_values(item.get("related_terms")),
                    components=self._list_values(item.get("components"), default=[name]),
                    context=self._list_values(item.get("context_terms")),
                    priority=self._clean_phrase(item.get("interview_priority")) or "Validate",
                    method="llm-grounded",
                    order=index,
                    specificity=9,
                )
            )
        return self._dedupe(drafts)

    def _merge(self, primary: list[_RequirementDraft], fallback: list[_RequirementDraft]) -> list[_RequirementDraft]:
        merged = list(primary)
        keys = {self._plain(item.name) for item in merged}
        components = {self._plain(component) for item in merged for component in item.components}
        for item in fallback:
            key = self._plain(item.name)
            item_components = {self._plain(value) for value in item.components}
            if key in keys or (item_components and item_components.intersection(components)):
                continue
            merged.append(item)
            keys.add(key)
            components.update(item_components)
        return self._dedupe(merged)

    def _select(self, drafts: list[_RequirementDraft], *, limit: int) -> list[_RequirementDraft]:
        importance_rank = {"Critical": 3, "High": 2, "Supporting": 1}
        ranked = sorted(
            self._dedupe(drafts),
            key=lambda item: (
                -importance_rank.get(item.importance, 1),
                -item.specificity,
                item.order,
                item.name.casefold(),
            ),
        )

        selected: list[_RequirementDraft] = []
        family_counts: dict[str, int] = {}
        for item in ranked:
            if len(selected) >= limit:
                break
            # Keep precise requirements; limit generic repetition within one family.
            family_count = family_counts.get(item.family, 0)
            if item.specificity <= 5 and family_count >= 2:
                continue
            selected.append(item)
            family_counts[item.family] = family_count + 1

        if len(selected) < min(limit, 5):
            for item in ranked:
                if item in selected:
                    continue
                selected.append(item)
                if len(selected) >= limit:
                    break
        return selected

    def _dedupe(self, drafts: list[_RequirementDraft]) -> list[_RequirementDraft]:
        result: list[_RequirementDraft] = []
        for item in drafts:
            key = self._plain(item.name)
            if not key or key in self._STOP_TERMS:
                continue
            duplicate = next((existing for existing in result if self._equivalent(existing, item)), None)
            if duplicate is None:
                item.aliases = self._unique(item.aliases + [item.name])
                item.related = self._unique(item.related)
                item.components = self._unique(item.components or [item.name])
                item.context = self._unique(item.context)
                result.append(item)
                continue
            duplicate.aliases = self._unique(duplicate.aliases + item.aliases + [item.name])
            duplicate.related = self._unique(duplicate.related + item.related)
            duplicate.components = self._unique(duplicate.components + item.components)
            duplicate.context = self._unique(duplicate.context + item.context)
            if item.specificity > duplicate.specificity:
                duplicate.name = item.name
                duplicate.category = item.category
                duplicate.family = item.family
                duplicate.kind = item.kind
                duplicate.source = item.source
                duplicate.specificity = item.specificity
            if self._importance_score(item.importance) > self._importance_score(duplicate.importance):
                duplicate.importance = item.importance
                duplicate.level = max(duplicate.level, item.level)
                duplicate.priority = item.priority
        return result

    def _equivalent(self, left: _RequirementDraft, right: _RequirementDraft) -> bool:
        left_name = self._plain(left.name)
        right_name = self._plain(right.name)
        if left_name == right_name:
            return True
        left_components = {self._plain(value) for value in left.components if self._plain(value)}
        right_components = {self._plain(value) for value in right.components if self._plain(value)}
        if left_components and right_components and left_components.intersection(right_components):
            return True
        # Containment is only used for precise product/method names in the
        # same family; broad token overlap would incorrectly merge distinct
        # dashboard axes such as data quality and reporting.
        if left.family == right.family and left.specificity >= 8 and right.specificity >= 8:
            if left_name in right_name or right_name in left_name:
                return True
        return False

    def _to_requirement(self, item: _RequirementDraft) -> TechnicalRequirement:
        return TechnicalRequirement(
            requirement_id=self._slug(item.name),
            name=item.name,
            category=item.category,
            family=item.family,
            requirement_kind=item.kind,
            importance=item.importance,
            required_level=round(max(0.0, min(5.0, item.level)), 1),
            source_excerpt=item.source[:400],
            aliases=tuple(item.aliases),
            related_terms=tuple(item.related),
            components=tuple(item.components),
            context_terms=tuple(item.context),
            interview_priority=item.priority,
            extraction_method=item.method,
        )

    def _named_terms(self, line: str) -> list[str]:
        clean = " ".join(str(line or "").split())
        values: list[str] = []

        patterns = (
            r"\b[A-Z]{2,}(?:[ /-][A-Z0-9]{1,8})*(?:\s+[A-Z][A-Za-z0-9+#.-]{1,30}){0,2}\b",
            r"\b[A-Z][a-z]+(?:[A-Z][A-Za-z0-9]+)+(?:\s+[A-Z0-9][A-Za-z0-9+#.-]*){0,2}\b",
            r"\b[A-Z][A-Za-z0-9+#.-]{2,30}\s+[A-Z]{2,}(?:\s+\d+)?\b",
            r"\b[A-Z][A-Za-z0-9+#.-]{2,30}\s+[A-Z][a-z][A-Za-z0-9+#.-]{2,30}(?:\s+\d+)?\b",
            r"\b[A-Za-z][A-Za-z0-9+#.-]*[/&][A-Za-z0-9+#./-]+\b",
        )
        for pattern in patterns:
            values.extend(match.group(0) for match in re.finditer(pattern, clean))
        values.extend(
            match.group(0)
            for match in re.finditer(
                r"\b(?:Lean\s+Six\s+Sigma|Six\s+Sigma|Agile|Scrum|Kanban)\b",
                clean,
                flags=re.I,
            )
        )

        for token in re.findall(r"\b[A-Za-z][A-Za-z0-9+#.-]{2,32}\b", clean):
            if (
                any(char.isdigit() for char in token)
                or any(char in token for char in "+#.")
                or (any(char.isupper() for char in token[1:]) and any(char.islower() for char in token))
                or (token.isupper() and len(token) >= 3)
            ):
                values.append(token)

        cleaned: list[str] = []
        for value in self._unique(values):
            term = self._clean_phrase(value)
            plain = self._plain(term)
            if plain in {"hr", "bi", "ai", "core hr"}:
                continue
            if re.match(r"^(?:lead|manage|design|ensure|support|provide|participate|carry)\b", term, flags=re.I):
                continue
            if self._valid_requirement_term(term):
                cleaned.append(term)

        # Keep maximal names (SAP SuccessFactors rather than SAP and
        # SuccessFactors; Power BI rather than BI).
        maximal: list[str] = []
        for term in sorted(cleaned, key=lambda value: (-len(self._plain(value)), cleaned.index(value))):
            plain = self._plain(term)
            if any(plain != self._plain(existing) and plain in self._plain(existing) for existing in maximal):
                continue
            maximal.append(term)
        maximal.sort(key=lambda value: clean.find(value) if clean.find(value) >= 0 else 9999)
        return maximal

    def _cue_terms(self, line: str) -> list[str]:
        values: list[str] = []
        for pattern in self._CUE_PATTERNS:
            for match in re.finditer(pattern, line, flags=re.I):
                captured = match.group(1)
                captured = re.split(r"\b(?:and the ability|while|who|that|to lead|to manage|to work)\b", captured, maxsplit=1, flags=re.I)[0]
                for item in self._split_list(captured):
                    if self._valid_requirement_term(item):
                        values.append(item)
        return self._unique(values)

    def _noun_capabilities(self, line: str) -> list[str]:
        clean = self._plain(line)
        results: list[str] = []
        for suffix in self._KIND_SUFFIXES:
            pattern = rf"\b([a-z][a-z0-9+#-]*(?:\s+[a-z][a-z0-9+#-]*){{0,3}}\s+{re.escape(suffix)})\b"
            for match in re.finditer(pattern, clean):
                phrase = match.group(1)
                phrase = re.sub(
                    r"^(?:of|in|with|for|and|the|experience in|expertise in|knowledge of|proficiency in|lead|own|manage|report|build|design)\s+",
                    "",
                    phrase,
                ).strip()
                if " to " in f" {phrase} " or " and " in f" {phrase} ":
                    continue
                if len(phrase.split()) >= 2 and self._valid_requirement_term(phrase):
                    results.append(phrase)
        return self._unique(results)

    def _split_list(self, value: str) -> list[str]:
        clean = re.sub(r"\([^)]{80,}\)", "", str(value or ""))
        parts = re.split(r"\s*[,;|•]\s*|\s+and\s+|\s+or\s+|\s+et\s+", clean, flags=re.I)
        results: list[str] = []
        for part in parts:
            part = re.sub(r"^(?:strong|excellent|good|advanced|solid|proven|demonstrated|working)\s+", "", part.strip(), flags=re.I)
            part = re.sub(r"^(?:knowledge|experience|expertise|proficiency|mastery|familiarity|skills?)\s+(?:in|with|of|on)\s+", "", part, flags=re.I)
            part = re.sub(r"\s+(?:is|are|will be)\s+(?:required|essential|preferred).*$", "", part, flags=re.I)
            part = self._clean_phrase(part)
            if 1 <= len(part.split()) <= 8:
                results.append(part)
        return results

    def _importance(self, line: str) -> tuple[str, float]:
        plain = self._plain(line)
        if any(self._plain(marker) in plain for marker in self._IMPORTANCE_PREFERRED):
            return "Supporting", 3.0
        if any(self._plain(marker) in plain for marker in self._IMPORTANCE_CRITICAL):
            return "Critical", 4.5
        if any(marker in plain for marker in ("lead", "design", "implement", "own", "ensure", "manage", "responsible")):
            return "High", 4.0
        return "High", 3.5

    def _importance_value(self, value: object) -> str:
        plain = self._plain(value)
        if "critical" in plain or "mandatory" in plain:
            return "Critical"
        if "support" in plain or "preferred" in plain:
            return "Supporting"
        return "High"

    @staticmethod
    def _importance_score(value: str) -> int:
        return {"Critical": 3, "High": 2, "Supporting": 1}.get(value, 1)

    def _family(self, context: str, term: str) -> tuple[str, str]:
        context_plain = self._plain(context)
        term_plain = self._plain(term)
        plain = self._plain(f"{context} {term}")
        # A named tool used to design reports/dashboards is a BI tool even
        # when the source data belongs to another domain (for example Core HR).
        if term_plain.endswith("sql") or term_plain in {"sql", "nosql"}:
            return "Data & Databases", "Data & Analytics"
        if term_plain.endswith(" bi") or (
            any(marker in context_plain for marker in ("report", "dashboard", "visualization", "visualisation", "kpi"))
            and len(term_plain.split()) >= 2
        ):
            return "Business Intelligence", "Data & Analytics"
        if re.fullmatch(r"[a-z]{3,6}", term_plain) and any(marker in context_plain for marker in ("across", "region", "market", "territory")):
            return "Market Experience", "Commercial & International"
        scored: list[tuple[int, int, str, str]] = []
        for order, (family, category, markers) in enumerate(self._FAMILY_RULES):
            score = 0
            for marker in markers:
                normalized = self._plain(marker)
                if normalized and self._contains_phrase(plain, normalized):
                    score += 3 if self._contains_phrase(self._plain(term), normalized) else 1
            if score:
                scored.append((score, -order, family, category))
        if scored:
            _score, _order, family, category = max(scored)
            return family, category
        if self._looks_like_certification(term, context):
            return "Professional Certifications", "Credentials"
        if self._looks_like_methodology(term, context):
            return "Methods & Frameworks", "Methods"
        return "Technical Tools & Platforms", "Technology & Tools"

    def _kind(self, term: str, context: str, family: str) -> str:
        plain_term = self._plain(term)
        plain_context = self._plain(context)
        if self._looks_like_certification(term, context):
            return "certification"
        if self._looks_like_methodology(term, context):
            return "methodology"
        if (
            str(term).strip().isupper()
            and len(plain_term) <= 8
            and len(str(term).strip().split()) == 1
            and any(marker in plain_context for marker in ("knowledge", "standard", "regulation", "reporting rules", "compliance"))
            and not any(marker in plain_context for marker in ("system", "software", "platform", "tool"))
        ):
            return "standard_or_regulation"
        if any(plain_term.endswith(f" {suffix}") for suffix in self._KIND_SUFFIXES):
            return "functional_capability"
        if family == "Applied Artificial Intelligence":
            return "technical_innovation"
        if family == "Market Experience":
            return "functional_capability"
        if family in {"HRIS Platforms", "Finance Systems", "CRM & Sales Platforms", "Supply Chain Systems"}:
            return "technical_platform"
        if family in {"Technical Tools & Platforms", "Business Intelligence", "Data & Databases", "Software Engineering", "Cloud & DevOps", "Cybersecurity", "Marketing Technology"}:
            return "technical_tool"
        return "general_capability"

    def _compose_name(
        self,
        term: str,
        context: str,
        domain: str,
        family: str,
        *,
        global_text: str = "",
    ) -> str:
        plain = self._plain(context)
        global_plain = self._plain(global_text)
        clean_term = self._clean_phrase(term)
        if clean_term == clean_term.casefold():
            clean_term = self._title_phrase(clean_term)
        if family == "Market Experience":
            return f"{clean_term} Market Experience"
        if family == "HRIS Platforms" and "core hr" in global_plain and "core hr" not in self._plain(clean_term):
            return f"{clean_term} & Core HR"
        if family == "Business Intelligence" and any(marker in plain for marker in ("report", "dashboard")):
            reporting = f"{domain} Reporting" if domain else "Reporting"
            if self._plain(reporting) not in self._plain(clean_term):
                return f"{clean_term} & {reporting}"
        return clean_term

    def _domain_capability_name(self, name: str, domain: str, plain: str) -> str:
        if name == "Project Leadership & Delivery" and domain == "HR" and "hris" in plain:
            return "HRIS Project Leadership"
        if name == "Data Quality & Governance" and domain == "HR" and "core hr" in plain:
            return "Data Quality & Core HR Reliability"
        return name

    def _domain_label(self, role_title: str, text: str) -> str:
        plain = self._plain(f"{role_title} {text[:1000]}")
        rules = (
            ("HR", ("hris", "human resources", "human resource", "talent management", "payroll")),
            ("Finance", ("financial controller", "finance manager", "accounting", "ifrs", "consolidation")),
            ("Software", ("software engineer", "developer", "backend", "frontend", "application engineer")),
            ("Sales", ("sales manager", "account executive", "business development", "commercial")),
            ("Supply Chain", ("supply chain", "logistics", "procurement", "inventory")),
            ("Marketing", ("marketing manager", "growth marketing", "digital marketing")),
            ("Operations", ("operations manager", "plant manager", "manufacturing", "maintenance")),
        )
        for label, markers in rules:
            if any(marker in plain for marker in markers):
                return label
        words = [word for word in self._clean_phrase(role_title).split() if word.casefold() not in {"senior", "manager", "lead", "director", "specialist", "officer", "head"}]
        return " ".join(words[:2]).title() if words else ""

    def _related_terms(self, context: str, term: str, family: str) -> list[str]:
        values = self._context_terms(context)
        for entity in self._named_terms(context):
            if self._plain(entity) != self._plain(term):
                values.append(entity)
        # Family names and adjacent family labels help candidate-side
        # transferability detection without enumerating product names.
        values.append(family)
        values.extend(self.adjacent_families(family))
        return self._unique(values)[:16]

    def _context_terms(self, value: str) -> list[str]:
        plain = self._plain(value)
        terms: list[str] = []
        for family, _category, markers in self._FAMILY_RULES:
            for marker in markers:
                if self._contains_phrase(plain, marker):
                    terms.append(marker)
                    terms.append(family)
        return self._unique(terms)

    def _aliases(self, term: str) -> list[str]:
        clean = self._clean_phrase(term)
        aliases = [clean]
        compact = re.sub(r"[^A-Za-z0-9+#]", "", clean)
        if compact and self._plain(compact) != self._plain(clean):
            aliases.append(compact)
        without_vendor = re.sub(r"^(?:microsoft|google|oracle|sap|ibm|amazon|aws)\s+", "", clean, flags=re.I)
        if without_vendor != clean and len(without_vendor) >= 3:
            aliases.append(without_vendor)
        return self._unique(aliases)

    def _looks_like_named_requirement(self, term: str, context: str) -> bool:
        clean = self._clean_phrase(term)
        plain = self._plain(clean)
        if not clean:
            return False
        if any(language in plain.split() for language in ("english", "french", "german", "spanish", "mandarin", "chinese", "arabic", "italian")):
            return False
        if plain in {"roi", "kpi", "hr", "bi", "ai"}:
            return False
        if re.match(r"^(?:lead|manage|design|ensure|support|provide|participate|carry|apply|own|build|create|launch)\b", clean, flags=re.I):
            return False
        if any(char in clean for char in "/+#.") or any(char.isdigit() for char in clean):
            return True
        if plain.endswith((" system", " systems", " platform", " platforms", " tool", " tools")):
            return True
        if clean.isupper() and 2 <= len(clean) <= 20:
            return True
        if any(char.isupper() for char in clean[1:]) and any(char.islower() for char in clean):
            return True
        if all(word[:1].isupper() for word in clean.split() if word):
            return True
        return False

    def _valid_requirement_term(self, value: object) -> bool:
        clean = self._clean_phrase(value)
        plain = self._plain(clean)
        if not clean or plain in self._STOP_TERMS:
            return False
        if len(clean) < 2 or len(clean) > 90 or len(clean.split()) > 10:
            return False
        if all(token in self._GENERIC_WORDS for token in plain.split()):
            return False
        if re.fullmatch(r"\d+(?:[.,]\d+)?", clean):
            return False
        return True

    def _is_noise_line(self, line: str) -> bool:
        plain = self._plain(line)
        if plain in self._SECTION_HEADINGS:
            return True
        if line.strip().isupper() and len(line.strip()) <= 65:
            return True
        if len(plain) < 3:
            return True
        if re.fullmatch(r"[\W\d_]+", line):
            return True
        return False

    def _looks_like_heading(self, line: str) -> bool:
        clean = line.strip()
        if not clean or len(clean) > 65:
            return False
        return clean.isupper() or self._plain(clean.rstrip(":")) in self._SECTION_HEADINGS or clean.endswith(":")

    def _looks_like_certification(self, term: str, context: str) -> bool:
        plain = self._plain(f"{term} {context}")
        return any(marker in plain for marker in ("certification", "certified", "certificate", "license", "licence"))

    def _looks_like_methodology(self, term: str, context: str) -> bool:
        plain = self._plain(f"{term} {context}")
        return any(marker in plain for marker in ("methodology", "framework", "method", "agile", "scrum", "lean", "six sigma"))

    def _lines(self, text: str) -> list[str]:
        raw_lines = [
            " ".join(raw_line.strip(" \t•*-–—").split())
            for raw_line in str(text or "").replace("\r", "\n").splitlines()
        ]
        raw_lines = [line for line in raw_lines if line]

        merged: list[str] = []
        buffer = ""
        for raw_index, line in enumerate(raw_lines):
            if not buffer:
                buffer = line
                continue
            if raw_index == 1 and not re.search(r"[.!?:]$", buffer) and len(buffer) <= 90:
                merged.append(buffer)
                buffer = line
                continue
            tail = re.split(r"[.!?]\s*", buffer)[-1].strip()
            continuation = (
                not re.search(r"[.!?:]$", buffer)
                and not self._looks_like_heading(buffer)
                and (
                    len(tail) < 95
                    or line[:1].islower()
                    or line.casefold().startswith(("and ", "or ", "et ", "with ", "including "))
                )
            )
            if continuation:
                buffer = f"{buffer} {line}"
            else:
                merged.append(buffer)
                buffer = line
        if buffer:
            merged.append(buffer)

        lines: list[str] = []
        for clean in merged:
            pieces = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])", clean)
            lines.extend(piece.strip() for piece in pieces if piece.strip())
        return lines

    def _clean_phrase(self, value: object) -> str:
        clean = " ".join(str(value or "").strip(" \t•*-–—:;,.()").split())
        return clean[:120]

    def _title_phrase(self, value: str) -> str:
        return " ".join(word.upper() if word in {"ai", "api", "seo", "crm", "erp", "sql", "s&op"} else word.capitalize() for word in self._clean_phrase(value).split())

    def _list_values(self, value: object, *, default: list[str] | None = None) -> list[str]:
        if isinstance(value, str):
            raw = [value]
        elif isinstance(value, (list, tuple, set)):
            raw = list(value)
        else:
            raw = list(default or [])
        return self._unique([self._clean_phrase(item) for item in raw if self._clean_phrase(item)])

    def _contains_phrase(self, plain_text: str, phrase: object) -> bool:
        needle = self._plain(phrase)
        if not needle:
            return False
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", plain_text))

    @staticmethod
    def _plain(value: object) -> str:
        text = unicodedata.normalize("NFKD", str(value or ""))
        text = "".join(char for char in text if not unicodedata.combining(char))
        text = text.casefold().replace("&", " and ")
        text = re.sub(r"[^a-z0-9+#]+", " ", text)
        return " ".join(text.split())

    @staticmethod
    def _slug(value: object) -> str:
        return re.sub(r"[^a-z0-9]+", "-", str(value or "item").casefold()).strip("-") or "item"

    def _unique(self, values: Iterable[object]) -> list[str]:
        results: list[str] = []
        seen: set[str] = set()
        for value in values or ():
            clean = self._clean_phrase(value)
            key = self._plain(clean)
            if not clean or not key or key in seen:
                continue
            seen.add(key)
            results.append(clean)
        return results
