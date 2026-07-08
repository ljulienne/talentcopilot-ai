from talentcopilot.document_intelligence.pipeline import DocumentIntelligencePipeline
from talentcopilot.extraction.skills_ontology import SkillsOntology
from talentcopilot.extraction.text_signals import TextSignalExtractor
from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.real_matching.models import RealMatchingInput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline


def test_skills_ontology_detects_french_and_english_synonyms():
    text = "Chef de projet SIRH avec conduite du changement, paie, GTA, reporting BO et API."
    skills = SkillsOntology().extract_skills(text)

    assert "HRIS" in skills
    assert "Project Management" in skills
    assert "Change Management" in skills
    assert "Payroll" in skills
    assert "Time Management" in skills
    assert "Reporting" in skills
    assert "API Integration" in skills


def test_text_signal_extractor_detects_years_languages_certifications():
    text = "11 years experience. Français English Mandarin. PMP and ITIL certified."
    extractor = TextSignalExtractor()

    assert extractor.extract_years_experience(text) == 11
    assert "French" in extractor.extract_languages(text)
    assert "English" in extractor.extract_languages(text)
    assert "Mandarin" in extractor.extract_languages(text)
    assert "PMP" in extractor.extract_certifications(text)
    assert "ITIL" in extractor.extract_certifications(text)


def test_candidate_extraction_is_richer_for_real_cv():
    cv = '''
Louis Julienne
Experience
11 years experience as HRIS Project Manager.
Led SIRH implementation, payroll interface, OCTIME GTA, Business Objects reporting and change management.
Skills
SIRH, paie, GTA, reporting, conduite du changement, API, stakeholder management.
Languages
French English Mandarin
Certifications
PHRi PMP
Achievements
Improved adoption by 35%.
'''
    analysis, candidate = DocumentIntelligencePipeline().analyze_text("cv.txt", cv)

    assert candidate.candidate_name == "Louis Julienne"
    assert "HRIS" in candidate.skills
    assert "Payroll" in candidate.skills
    assert "Time Management" in candidate.skills
    assert "Change Management" in candidate.skills


def test_job_extraction_detects_real_requirements():
    job = '''
Responsable SIRH Groupe
Missions
Piloter les projets SIRH, coordonner les parties prenantes et accompagner le changement.
Profil
Minimum 8 ans d'expérience. Compétences requises: SIRH, gestion de projet, paie, reporting, conduite du changement.
Langues
Français et anglais.
'''
    analysis = JobIntelligencePipeline().analyze_text("job.txt", job)
    profile = analysis.role_profile

    assert "HRIS" in profile.required_skills
    assert "Project Management" in profile.required_skills
    assert "Payroll" in profile.required_skills
    assert "Reporting" in profile.required_skills
    assert profile.minimum_years_experience == 8


def test_real_matching_improves_with_french_real_inputs():
    output = RealMatchingPipeline().run(
        RealMatchingInput(
            candidate_filename="cv.txt",
            candidate_text="Louis Julienne\n11 ans d'expérience SIRH paie GTA reporting conduite du changement gestion de projet.",
            job_filename="job.txt",
            job_text="Responsable SIRH\nProfil\nMinimum 8 ans. SIRH gestion de projet paie reporting conduite du changement.",
            expected_salary=90000,
        )
    )

    assert output.decision_output.profile.fit_score is not None
    assert output.decision_output.profile.fit_score >= 50
    assert output.decision_output.profile.recommendation != "Reject"
