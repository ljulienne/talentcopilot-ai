from talentcopilot.semantic_intelligence.models import SkillConcept


class SkillGraph:
    def __init__(self):
        self.concepts = [
            SkillConcept("HRIS", ["hris", "sirh", "human resources information system", "système d'information rh"], "HR Technology", "Digital HR", ["Workday", "SAP SuccessFactors", "Oracle HCM", "Talentsoft"]),
            SkillConcept("Workday", ["workday", "workday hcm"], "HR Technology", "HRIS", ["HRIS"]),
            SkillConcept("SAP SuccessFactors", ["successfactors", "sap successfactors", "sap sf"], "HR Technology", "HRIS", ["HRIS"]),
            SkillConcept("Oracle HCM", ["oracle hcm", "oracle cloud hcm"], "HR Technology", "HRIS", ["HRIS"]),
            SkillConcept("Talentsoft", ["talentsoft", "cegid talentsoft"], "HR Technology", "HRIS", ["HRIS"]),
            SkillConcept("Payroll", ["payroll", "paie", "gestion de la paie", "sedit", "sage paie"], "HR Operations", "HR Operations", ["HRIS"]),
            SkillConcept("Time Management", ["time management", "gta", "gestion des temps", "octime", "workforce management"], "HR Operations", "HR Operations", ["HRIS", "Payroll"]),
            SkillConcept("Reporting", ["reporting", "business objects", "bo", "power bi", "dashboard", "kpi", "analytics"], "Analytics", "Data", ["Data Analysis"]),
            SkillConcept("Data Analysis", ["data analysis", "analyse de données", "people analytics", "hr analytics"], "Analytics", "Data", ["Reporting"]),
            SkillConcept("Project Management", ["project management", "gestion de projet", "pilotage projet", "chef de projet"], "Management", "Delivery", ["Stakeholder Management", "Change Management"]),
            SkillConcept("Stakeholder Management", ["stakeholder management", "parties prenantes", "gestion des parties prenantes", "relations métiers"], "Management", "Delivery", ["Project Management"]),
            SkillConcept("Change Management", ["change management", "conduite du changement", "accompagnement du changement", "adoption"], "Transformation", "Delivery", ["Project Management"]),
            SkillConcept("Leadership", ["leadership", "management d'équipe", "team management", "encadrement"], "Management", "Leadership", ["Project Management"]),
            SkillConcept("Recruitment", ["recruitment", "recrutement", "ats", "talent acquisition"], "Talent Acquisition", "HR", ["HRIS"]),
            SkillConcept("Learning", ["learning", "formation", "lms"], "Talent Management", "HR", ["HRIS"]),
            SkillConcept("Performance Management", ["performance management", "entretiens annuels", "goal setting"], "Talent Management", "HR", ["HRIS"]),
        ]
        self._by_canonical = {c.canonical.lower(): c for c in self.concepts}

    def normalize(self, skill: str) -> str:
        lower = (skill or "").strip().lower()
        for concept in self.concepts:
            if lower == concept.canonical.lower() or lower in [a.lower() for a in concept.aliases]:
                return concept.canonical
        return (skill or "").strip()

    def get(self, skill: str) -> SkillConcept | None:
        return self._by_canonical.get(self.normalize(skill).lower())

    def family(self, skill: str) -> str | None:
        concept = self.get(skill)
        return concept.family if concept else None

    def are_related(self, left: str, right: str) -> bool:
        l = self.get(left)
        r = self.get(right)
        if not l or not r:
            return False
        return (
            l.canonical == r.canonical
            or l.parent == r.canonical
            or r.parent == l.canonical
            or r.canonical in l.related
            or l.canonical in r.related
            or l.family == r.family
        )
