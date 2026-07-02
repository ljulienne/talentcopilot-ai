from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class SearchEngine(ABC):
    @abstractmethod
    def search(
        self,
        talents: List[Dict[str, Any]],
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        pass
