from dataclasses import dataclass, field
from typing import List


@dataclass
class ProductWorkspace:
    name: str
    question: str
    value: str


@dataclass
class ProductPersona:
    name: str
    need: str
    workspace: str


@dataclass
class ProductOverview:
    tagline: str
    value_proposition: str
    principles: List[str] = field(default_factory=list)
    workspaces: List[ProductWorkspace] = field(default_factory=list)
    personas: List[ProductPersona] = field(default_factory=list)
    demo_flow: List[str] = field(default_factory=list)
