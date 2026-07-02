from __future__ import annotations

import os
import logging
from typing import Dict

from openai import OpenAI
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from talentcopilot.ai.recruiter_prompts import build_recruiter_prompt


logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("TALENTCOPILOT_OPENAI_MODEL", "gpt-4.1-mini")
DEFAULT_TIMEOUT_SECONDS = 45


def is_openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _fallback_response(message: str) -> Dict[str, str]:
    return {
        "source": "local",
        "prompt_type": "fallback",
        "answer": message,
    }


def generate_openai_recruiter_answer(
    context: dict,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, str]:
    if not is_openai_available():
        return _fallback_response(
            "OpenAI is not configured. Please set OPENAI_API_KEY to enable generative recruiter reasoning."
        )

    prompt = build_recruiter_prompt(context)

    try:
        client = OpenAI(timeout=timeout_seconds)

        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": prompt["system_prompt"],
                },
                {
                    "role": "user",
                    "content": prompt["user_prompt"],
                },
            ],
        )

        answer = getattr(response, "output_text", None)

        if not answer:
            return _fallback_response(
                "OpenAI returned an empty response. TalentCopilot used the local reasoning result instead."
            )

        return {
            "source": "openai",
            "prompt_type": prompt["prompt_type"],
            "answer": answer,
        }

    except RateLimitError:
        logger.exception("OpenAI rate limit or quota error.")
        return _fallback_response(
            "OpenAI quota or rate limit was reached. TalentCopilot used local reasoning instead."
        )

    except APITimeoutError:
        logger.exception("OpenAI request timed out.")
        return _fallback_response(
            "OpenAI request timed out. TalentCopilot used local reasoning instead."
        )

    except APIConnectionError:
        logger.exception("OpenAI connection error.")
        return _fallback_response(
            "OpenAI connection failed. TalentCopilot used local reasoning instead."
        )

    except APIStatusError as exc:
        logger.exception("OpenAI API status error: %s", exc)
        return _fallback_response(
            f"OpenAI returned an API error ({exc.status_code}). TalentCopilot used local reasoning instead."
        )

    except Exception:
        logger.exception("Unexpected OpenAI error.")
        return _fallback_response(
            "Unexpected OpenAI error. TalentCopilot used local reasoning instead."
        )
