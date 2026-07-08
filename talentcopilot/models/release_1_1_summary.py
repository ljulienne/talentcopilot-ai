from dataclasses import dataclass, field
from typing import List


@dataclass
class ReleaseModule:
    name: str
    status: str
    value: str


@dataclass
class BlueprintReadinessItem:
    name: str
    status: str
    detail: str


@dataclass
class Release11Summary:
    title: str
    version: str
    product_message: str
    modules: List[ReleaseModule] = field(default_factory=list)
    blueprint_readiness: List[BlueprintReadinessItem] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
