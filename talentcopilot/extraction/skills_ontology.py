import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SkillConcept:
    canonical: str
    aliases: List[str]
    category: str = "General"


class SkillsOntology:
    def __init__(self):
        self.concepts = [
            SkillConcept("HRIS", ["hris", "sirh", "système d'information rh", "systèmes d'information rh", "human resources information system"], "HR Tech"),
            SkillConcept("Payroll", ["payroll", "paie", "gestion de la paie", "sedit", "sage paie"], "HR Operations"),
            SkillConcept("Time Management", ["time management", "gta", "gestion des temps", "octime", "workforce management"], "HR Operations"),
            SkillConcept("Project Management", ["project management", "gestion de projet", "pilotage projet", "chef de projet", "project manager"], "Management"),
            SkillConcept("Stakeholder Management", ["stakeholder management", "parties prenantes", "gestion des parties prenantes", "relations métiers", "business stakeholders"], "Management"),
            SkillConcept("Change Management", ["change management", "conduite du changement", "accompagnement du changement", "change adoption"], "Transformation"),
            SkillConcept("Leadership", ["leadership", "management d'équipe", "team management", "managed a team", "encadrement", "team lead"], "Management"),
            SkillConcept("Reporting", ["reporting", "business objects", "bo", "power bi", "tableau", "kpi", "dashboard", "dashboards"], "Analytics"),
            SkillConcept("Data Analysis", ["data analysis", "analyse de données", "analytics", "people analytics", "hr analytics"], "Analytics"),
            SkillConcept("API Integration", ["api", "interface", "integration", "intégration", "web service", "webservice", "rest api"], "Technology"),
            SkillConcept("SAP SuccessFactors", ["successfactors", "sap successfactors", "sap sf"], "HR Tech"),
            SkillConcept("Workday", ["workday"], "HR Tech"),
            SkillConcept("Oracle HCM", ["oracle hcm", "oracle cloud hcm"], "HR Tech"),
            SkillConcept("Talentsoft", ["talentsoft", "cegid talentsoft"], "HR Tech"),
            SkillConcept("Recruitment", ["recruitment", "recrutement", "ats", "applicant tracking"], "Talent Acquisition"),
            SkillConcept("Learning", ["learning", "formation", "lms", "learning management"], "Talent Management"),
            SkillConcept("Performance Management", ["performance management", "performance", "entretiens annuels", "goal setting", "objectives"], "Talent Management"),
            SkillConcept("Onboarding", ["onboarding", "intégration collaborateur", "employee onboarding"], "HR Operations"),
            SkillConcept("International Experience", ["international", "global", "multi-country", "multicountry", "chine", "china", "asia", "europe"], "Context"),
            SkillConcept("French", ["french", "français", "francais"], "Language"),
            SkillConcept("English", ["english", "anglais"], "Language"),
            SkillConcept("Mandarin", ["mandarin", "chinese", "chinois", "中文", "普通话"], "Language"),
        ]

    def extract_skills(self, text: str) -> List[str]:
        lower = (text or "").lower()
        found = []
        for concept in self.concepts:
            for alias in concept.aliases:
                pattern = r"(?<![a-zA-Z])" + re.escape(alias.lower()) + r"(?![a-zA-Z])"
                if re.search(pattern, lower):
                    found.append(concept.canonical)
                    break
        return list(dict.fromkeys(found))

    def categories(self, skills: List[str]) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        for skill in skills:
            concept = next((c for c in self.concepts if c.canonical == skill), None)
            category = concept.category if concept else "General"
            result.setdefault(category, []).append(skill)
        return result
