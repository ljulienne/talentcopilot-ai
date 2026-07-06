from typing import Any, Dict, List

from talentcopilot.enterprise_demo.repository import EnterpriseDemoRepository


class EnterpriseCandidateFactory:
    """
    Creates realistic enterprise candidate profiles from demo personas.
    """

    def __init__(self, repository: EnterpriseDemoRepository | None = None):
        self.repository = repository or EnterpriseDemoRepository()

    def generate_candidates(self) -> List[Dict[str, Any]]:
        personas = self.repository.personas()

        candidates = []

        base_names = [
            ("Claire", "Martin", "France", "Paris"),
            ("Li", "Wei", "Singapore", "Singapore"),
            ("Michael", "Brown", "United Kingdom", "London"),
            ("Sofia", "Rossi", "Italy", "Milan"),
            ("David", "Smith", "United States", "New York"),
            ("Emma", "Wang", "China", "Shanghai"),
            ("Julien", "Moreau", "France", "Lyon"),
            ("Anna", "Schneider", "Germany", "Berlin"),
            ("Carlos", "Mendes", "Portugal", "Lisbon"),
            ("Mei", "Zhang", "China", "Shenzhen"),
            ("Thomas", "Leroy", "France", "Toulouse"),
            ("Aisha", "Khan", "United Arab Emirates", "Dubai"),
        ]

        skill_sets = [
            ["SK001", "SK002", "SK013", "SK017", "SK018"],
            ["SK004", "SK011", "SK015", "SK018", "SK019"],
            ["SK020", "SK021", "SK022", "SK024", "SK026"],
            ["SK010", "SK037", "SK038", "SK040"],
            ["SK003", "SK005", "SK012", "SK013"],
            ["SK029", "SK030", "SK031", "SK032", "SK033"],
            ["SK035", "SK036", "SK017", "SK016"],
            ["SK003", "SK006", "SK034", "SK039"],
            ["SK015", "SK014", "SK016", "SK018"],
            ["SK024", "SK025", "SK028", "SK020"],
            ["SK001", "SK010", "SK013", "SK040"],
            ["SK018", "SK019", "SK016", "SK017"],
        ]

        language_sets = [
            [{"language_id": "LANG001", "level": "Native"}, {"language_id": "LANG002", "level": "C1"}],
            [{"language_id": "LANG003", "level": "Native"}, {"language_id": "LANG002", "level": "C2"}],
            [{"language_id": "LANG002", "level": "Native"}],
            [{"language_id": "LANG006", "level": "Native"}, {"language_id": "LANG002", "level": "C1"}],
            [{"language_id": "LANG002", "level": "Native"}],
            [{"language_id": "LANG003", "level": "Native"}, {"language_id": "LANG002", "level": "C1"}, {"language_id": "LANG001", "level": "B2"}],
            [{"language_id": "LANG001", "level": "Native"}, {"language_id": "LANG002", "level": "B2"}],
            [{"language_id": "LANG005", "level": "Native"}, {"language_id": "LANG002", "level": "C1"}],
            [{"language_id": "LANG007", "level": "Native"}, {"language_id": "LANG002", "level": "C1"}, {"language_id": "LANG001", "level": "B2"}],
            [{"language_id": "LANG003", "level": "Native"}, {"language_id": "LANG002", "level": "C1"}],
            [{"language_id": "LANG001", "level": "Native"}, {"language_id": "LANG002", "level": "C1"}],
            [{"language_id": "LANG002", "level": "C2"}, {"language_id": "LANG004", "level": "B2"}],
        ]

        certification_sets = [
            ["CERT001", "CERT002"],
            ["CERT001", "CERT008"],
            ["CERT006"],
            [],
            ["CERT007"],
            ["CERT003", "CERT004"],
            ["CERT001"],
            ["CERT007"],
            ["CERT001"],
            ["CERT006", "CERT009"],
            ["CERT002"],
            ["CERT005"],
        ]

        for index, persona in enumerate(personas[:12]):
            first_name, last_name, country, city = base_names[index]
            years = 5 + index

            candidates.append({
                "id": f"CAND{index + 1:03d}",
                "persona_id": persona["id"],
                "first_name": first_name,
                "last_name": last_name,
                "name": f"{first_name} {last_name}",
                "country": country,
                "city": city,
                "years_experience": years,
                "current_title": persona["name"],
                "skills": skill_sets[index],
                "languages": language_sets[index],
                "certifications": certification_sets[index],
                "salary_expectation_eur": 60000 + (index * 6500),
                "remote_preference": "Hybrid" if index % 2 == 0 else "Remote",
                "mobility": "International" if index in [1, 5, 8, 11] else "Regional",
                "leadership_years": max(0, years - 6),
                "summary": persona["description"],
                "risks": persona.get("typical_risks", []),
                "strengths": persona.get("typical_strengths", []),
            })

        return candidates
