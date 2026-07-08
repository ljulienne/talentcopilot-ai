from talentcopilot.ai_core.models import PromptTemplate


class PromptManager:
    def __init__(self):
        self._prompts = {
            "candidate.extract.v1": PromptTemplate(
                prompt_id="candidate.extract.v1",
                version="1.0",
                purpose="Extract structured candidate information from a CV section.",
                expected_schema="CandidateProfile",
                template=(
                    "You are an HR document extraction system. "
                    "Extract structured candidate information from the text. "
                    "Return only valid JSON matching the expected schema.\n\n"
                    "TEXT:\n{input_text}"
                ),
            ),
            "job.extract.v1": PromptTemplate(
                prompt_id="job.extract.v1",
                version="1.0",
                purpose="Extract structured job requirements from a job description.",
                expected_schema="RoleProfile",
                template=(
                    "You are an HR job description extraction system. "
                    "Extract structured role requirements. "
                    "Return only valid JSON matching the expected schema.\n\n"
                    "TEXT:\n{input_text}"
                ),
            ),
        }

    def get(self, prompt_id: str) -> PromptTemplate:
        if prompt_id not in self._prompts:
            raise KeyError(f"Prompt not found: {prompt_id}")
        return self._prompts[prompt_id]

    def render(self, prompt_id: str, input_text: str, variables: dict | None = None) -> str:
        variables = variables or {}
        template = self.get(prompt_id).template
        return template.format(input_text=input_text, **variables)

    def list_prompts(self) -> list[PromptTemplate]:
        return list(self._prompts.values())

    def register(self, prompt: PromptTemplate) -> None:
        self._prompts[prompt.prompt_id] = prompt
