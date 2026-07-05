from dataclasses import dataclass, field
from typing import Dict


@dataclass
class HiringStrategy:
    strategy_id: str
    name: str
    description: str = ""
    priorities: Dict[str, int] = field(default_factory=dict)
    is_default: bool = False
