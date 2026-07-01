
from talentcopilot.parsers.pdf_parser import extract_text_from_pdf
from talentcopilot.engines.job_builder import build_job_from_text
from talentcopilot.engines.candidate_builder import build_candidate_from_cv_text
from talentcopilot.engines.matching_engine import match_candidate_to_job


def analyze_recruitment_batch(job_file, cv_files):
    job_result = extract_text_from_pdf(job_file)

    if not job_result["success"]:
        return {
            "success": False,
            "job": None,
            "results": [],
            "errors": [
                {
                    "file": getattr(job_file, "name", "job_file"),
                    "error": job_result["error"]
                }
            ]
        }

    job = build_job_from_text(job_result["text"])

    results = []
    errors = []

    for cv_file in cv_files:
        cv_result = extract_text_from_pdf(cv_file)

        if not cv_result["success"]:
            errors.append({
                "file": getattr(cv_file, "name", "cv_file"),
                "error": cv_result["error"]
            })
            continue

        candidate = build_candidate_from_cv_text(
            cv_result["text"],
            fallback_name=getattr(cv_file, "name", "Unknown Candidate")
        )

        match_result = match_candidate_to_job(candidate, job)

        results.append({
            "file": getattr(cv_file, "name", "cv_file"),
            "candidate": candidate,
            "match_result": match_result
        })

    results = sorted(
        results,
        key=lambda x: x["match_result"].overall_score,
        reverse=True
    )

    return {
        "success": True,
        "job": job,
        "results": results,
        "errors": errors
    }
