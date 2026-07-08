CANDIDATE_EXTRACTION_PROMPT = '''
You are TalentCopilot's CV extraction engine.

Extract structured information from the CV text.

Rules:
- Return only data supported by the CV.
- Do not invent missing information.
- If a value is missing, return null, 0, or an empty list.
- Candidate name must be the person's name, not a section title.
- Section titles such as "About Me", "Professional Summary", "Signature HR Qualifications", "Experience", "Skills" are not candidate names.
- Remove credentials from the candidate name. Example: "LORETTA DANIELSON, MBA, SPHR" -> "Loretta Danielson".
- Extract evidence-rich skills, technologies, certifications, achievements and responsibilities.
- Infer seniority only when supported by role titles and experience.

CV TEXT:
{text}
'''

ROLE_EXTRACTION_PROMPT = '''
You are TalentCopilot's job description extraction engine.

Extract structured role requirements from the job description.

Rules:
- Return only data supported by the job description.
- Do not invent missing requirements.
- Separate required skills from preferred skills when possible.
- Extract minimum experience and salary range only if present.
- Preserve responsibilities as short action-oriented statements.

JOB DESCRIPTION TEXT:
{text}
'''
