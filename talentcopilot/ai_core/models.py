from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AIModelSpec:
    provider: str
    model: str
    purpose: str
    input_cost_per_1k_tokens: float = 0.0
    output_cost_per_1k_tokens: float = 0.0
    supports_structured_output: bool = True


@dataclass
class PromptTemplate:
    prompt_id: str
    version: str
    purpose: str
    template: str
    expected_schema: str = ""


@dataclass
class AIRequest:
    task: str
    prompt_id: str
    input_text: str
    variables: Dict[str, Any] = field(default_factory=dict)
    preferred_model: Optional[str] = None
    require_structured_output: bool = True


@dataclass
class AIUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: int = 0
    cache_hit: bool = False


@dataclass
class AIResponse:
    task: str
    model: str
    content: str
    structured_data: Dict[str, Any] = field(default_factory=dict)
    usage: AIUsage = field(default_factory=AIUsage)
    prompt_version: str = ""
    status: str = "OK"


@dataclass
class StructuredOutputEnvelope:
    schema_name: str
    data: Dict[str, Any]
    validation_status: str = "Not validated"
    errors: list[str] = field(default_factory=list)


@dataclass
class AIEvent:
    event_type: str
    task: str
    model: str
    prompt_id: str
    status: str
    cost: float = 0.0
    latency_ms: int = 0
    detail: str = ""
