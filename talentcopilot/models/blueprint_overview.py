from dataclasses import dataclass, field
from typing import List


@dataclass
class BlueprintPrinciple:
    name: str
    detail: str


@dataclass
class BlueprintLayer:
    name: str
    purpose: str


@dataclass
class BlueprintOverview:
    title: str
    positioning: str
    principles: List[BlueprintPrinciple] = field(default_factory=list)
    layers: List[BlueprintLayer] = field(default_factory=list)
    next_chapters: List[str] = field(default_factory=list)
