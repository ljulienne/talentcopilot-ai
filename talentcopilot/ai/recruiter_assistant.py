from __future__ import annotations

from typing import Any, Dict, List


def _get_results(recruitment: Dict[str, Any]) -> List[Dict[str, Any]]:
    batch = recruitment.get("analysis_batch") or {}
    if not isinstance(batch, dict):
        return []
    return batch.get("results") or []


def _get_match(result: Dict[str, Any]) -> Dict[str, Any]:
    match = result.get("match_result") or {}
    return match if isinstance(match, dict) else vars(match)


def _get_candidate(result: Dict[str, Any]) -> Dict[str, Any]:
    candidate = result.get("candidate") or {}
    return candidate if isinstance(candidate, dict) else vars(candidate)


def _score(result: Dict[str, Any]) -> int:
    return int(_get_match(result).get("overall_score", 0) or 0)


def _confidence(result: Dict[str, Any]) -> int:
    return int(_get_match(result).get("confidence_score", 0) or 0)


def _name(result: Dict[str, Any]) -> str:
    return _get_candidate(result).get("name", "Unknown Candidate")


def answer_recruiter_question(question: str, recruitment: Dict[str, Any] | None) -> str:
    if not recruitment:
        return "No active recruitment is currently loaded. Please create or open a recruitment first."

    results = _get_results(recruitment)

    if not results:
        return "This recruitment does not contain analyzed candidates yet. Please run the candidate analysis first."

    q = question.lower().strip()

    if not q:
        return "Please enter a question about the current recruitment."

    sorted_results = sorted(results, key=_score, reverse=True)

    if any(keyword in q for keyword in ["top", "best", "first", "highest", "ranked first"]):
        best = sorted_results[0]
        match = _get_match(best)
        return (
            f"The strongest candidate is **{_name(best)}** with a match score of "
            f"**{_score(best)}%** and an AI confidence score of **{_confidence(best)}%**.\n\n"
            f"Recommendation: **{match.get('recommendation', 'No recommendation available')}**.\n\n"
            f"{match.get('executive_summary', '')}"
        )

    if "above 90" in q or "over 90" in q or "90%" in q:
        candidates = [r for r in sorted_results if _score(r) >= 90]
        if not candidates:
            return "No candidate scored 90% or higher."
        lines = [f"- **{_name(r)}** — {_score(r)}%" for r in candidates]
        return "Candidates scoring **90% or higher**:\n\n" + "\n".join(lines)

    if "above 85" in q or "over 85" in q or "85%" in q:
        candidates = [r for r in sorted_results if _score(r) >= 85]
        if not candidates:
            return "No candidate scored 85% or higher."
        lines = [f"- **{_name(r)}** — {_score(r)}%" for r in candidates]
        return "Candidates scoring **85% or higher**:\n\n" + "\n".join(lines)

    if "average" in q or "avg" in q:
        avg = round(sum(_score(r) for r in results) / len(results))
        return f"The average match score for this recruitment is **{avg}%** across **{len(results)}** candidate(s)."

    if "confidence" in q:
        avg_conf = round(sum(_confidence(r) for r in results) / len(results))
        return f"The average AI confidence score is **{avg_conf}%** across **{len(results)}** candidate(s)."

    if "ranking" in q or "rank" in q or "list" in q:
        lines = [
            f"{index}. **{_name(result)}** — {_score(result)}%"
            for index, result in enumerate(sorted_results, start=1)
        ]
        return "Current candidate ranking:\n\n" + "\n".join(lines)

    if "interview" in q:
        top_three = sorted_results[:3]
        lines = [
            f"- **{_name(result)}** — {_score(result)}% match"
            for result in top_three
        ]
        return (
            "I recommend starting interviews with these candidates:\n\n"
            + "\n".join(lines)
            + "\n\nThey have the strongest match scores in the current recruitment."
        )

    return (
        "I can answer questions such as:\n\n"
        "- Who is the best candidate?\n"
        "- Who scored above 90%?\n"
        "- What is the average score?\n"
        "- Show me the ranking.\n"
        "- Who should I interview first?\n\n"
        "More advanced reasoning will be added in the next sprint with OpenAI integration."
    )
