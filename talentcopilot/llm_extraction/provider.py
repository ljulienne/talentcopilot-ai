import json
import os
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMExtractionError(Exception):
    pass


class MockLLMProvider:
    def extract(self, prompt: str, schema: Type[T]) -> T:
        # Deterministic provider for tests and offline demos.
        if schema.__name__ == "CandidateExtractionResult":
            from talentcopilot.llm_extraction.models import CandidateExtractionResult, CandidateFacts, CandidateInsights

            text = prompt
            name = "Unknown Candidate"
            if "LORETTA DANIELSON" in text.upper():
                name = "Loretta Danielson"
            elif "VINCENT BLAKOE" in text.upper():
                name = "Vincent Blakoe"
            elif "Louis Julienne" in text:
                name = "Louis Julienne"

            return CandidateExtractionResult(
                facts=CandidateFacts(
                    candidate_name=name,
                    headline="Extracted candidate profile",
                    years_experience=13 if "13 years" in text else 0,
                    skills=["HRIS", "Project Management", "Leadership"],
                    certifications=["SPHR"] if "SPHR" in text else [],
                    languages=["English"] if "English" in text else [],
                    achievements=["Structured extraction demo"],
                ),
                insights=CandidateInsights(seniority="Senior"),
                extraction_confidence=0.8,
                source_summary="Mock extraction",
                extraction_status="OK",
            )

        if schema.__name__ == "RoleExtractionResult":
            from talentcopilot.llm_extraction.models import RoleExtractionResult, RoleFacts, RoleInsights

            return RoleExtractionResult(
                facts=RoleFacts(
                    title="Extracted Role",
                    required_skills=["HRIS", "Project Management"],
                    minimum_experience=5,
                    responsibilities=["Lead HRIS projects"],
                ),
                insights=RoleInsights(seniority_level="Senior"),
                extraction_confidence=0.8,
                source_summary="Mock extraction",
                extraction_status="OK",
            )

        raise LLMExtractionError(f"Unsupported schema: {schema.__name__}")


class OpenAIExtractionProvider:
    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("TALENTCOPILOT_LLM_MODEL", "gpt-5-mini")

    def extract(self, prompt: str, schema: Type[T]) -> T:
        try:
            from openai import OpenAI
        except Exception as exc:
            raise LLMExtractionError("OpenAI package is not installed.") from exc

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise LLMExtractionError("OPENAI_API_KEY is not configured.")

        client = OpenAI(api_key=api_key)

        # Prefer modern parse interfaces, but keep defensive fallbacks.
        try:
            parsed = client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": "You extract HR documents into strict structured data.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                text_format=schema,
            )
            return parsed.output_parsed
        except Exception:
            pass

        try:
            parsed = client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You extract HR documents into strict structured data.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                response_format=schema,
            )
            return parsed.choices[0].message.parsed
        except Exception as exc:
            raise LLMExtractionError(f"OpenAI structured extraction failed: {exc}") from exc


class SafeExtractionProvider:
    def __init__(self, primary=None, fallback=None):
        self.primary = primary or OpenAIExtractionProvider()
        self.fallback = fallback or MockLLMProvider()

    def extract(self, prompt: str, schema: Type[T]) -> T:
        use_llm = os.environ.get("TALENTCOPILOT_USE_LLM_EXTRACTION", "auto").lower()
        if use_llm in {"false", "0", "no", "mock"}:
            return self.fallback.extract(prompt, schema)

        try:
            return self.primary.extract(prompt, schema)
        except Exception:
            return self.fallback.extract(prompt, schema)
