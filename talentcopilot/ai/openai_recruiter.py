from __future__ import annotations

import os
from typing import Dict

from openai import OpenAI

from talentcopilot.ai.recruiter_prompts import build_recruiter_prompt


DEFAULT_MODEL = "gpt-4.1-mini"


def is_openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def generate_openai_recruiter_answer(
    context: dict,
    model: str = DEFAULT_MODEL,
) -> Dict[str, str]:
    if not is_openai_available():
        return {
            "source": "local",
            "answer": "OpenAI is not configured. Please set OPENAI_API_KEY to enable generative recruiter reasoning.",
        }

    prompt = build_recruiter_prompt(context)

    client = OpenAI()

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

    return {
        "source": "openai",
        "prompt_type": prompt["prompt_type"],
        "answer": response.output_text,
    }
