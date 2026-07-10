from __future__ import annotations

import pandas as pd

from .graph import OrganizationGraph


def edges_dataframe(graph: OrganizationGraph) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "source": graph.employees[edge.source].name,
            "target": graph.employees[edge.target].name,
            "source_department": graph.employees[edge.source].department,
            "target_department": graph.employees[edge.target].department,
            "relation": edge.relation,
            "weight": edge.weight,
            "evidence": edge.evidence,
        }
        for edge in graph.edges
    ])
