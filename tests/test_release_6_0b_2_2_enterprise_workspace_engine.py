from __future__ import annotations

import ast
from pathlib import Path

from talentcopilot.ui.design_system.v2.workspace import (
    EnterpriseWorkspaceModel,
    WorkspaceAction,
    WorkspaceCard,
    WorkspaceMetric,
    WorkspaceSection,
    WorkspaceStatusStep,
    clamp_readiness,
)


def test_workspace_model_accepts_presentation_state() -> None:
    model = EnterpriseWorkspaceModel(
        title="Senior Sales Manager APAC",
        eyebrow="Recruitment mission",
        status="Decision preparation",
        readiness=91,
        summary="Decision-ready mission.",
        metrics=(WorkspaceMetric("Candidates", "5", "5 analysed"),),
        steps=(WorkspaceStatusStep("Ranking complete", complete=True),),
        insights=(WorkspaceCard("Lead candidate", "Candidate A leads."),),
        actions=(WorkspaceAction("Prepare interview", "prepare_interview", primary=True),),
        sections=(WorkspaceSection("ranking", "Ranking"),),
    )
    assert model.title == "Senior Sales Manager APAC"
    assert model.readiness == 91
    assert model.metrics[0].value == "5"
    assert model.steps[0].complete is True


def test_readiness_is_safely_clamped() -> None:
    assert clamp_readiness(None) is None
    assert clamp_readiness(-4) == 0
    assert clamp_readiness(45) == 45
    assert clamp_readiness(104) == 100


def test_workspace_engine_has_no_business_engine_imports() -> None:
    path = Path("talentcopilot/ui/design_system/v2/workspace.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)

    forbidden = ("matching", "ranking", "decision_core", "enterprise_pipeline", "fit_intelligence")
    assert not any(any(token in module for token in forbidden) for module in imports)


def test_streamlit_is_not_imported_at_module_level() -> None:
    path = Path("talentcopilot/ui/design_system/v2/workspace.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    module_imports = [
        node for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    rendered = ast.unparse(ast.Module(body=module_imports, type_ignores=[]))
    assert "streamlit" not in rendered
