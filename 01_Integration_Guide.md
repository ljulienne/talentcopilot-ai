# TalentCopilot-AI — Mega Sprint 14
## v0.6 Explainable AI / AI Governance Layer

Ce sprint ajoute une couche autonome d'explicabilité et de gouvernance IA.

## Objectif

Transformer les résultats de matching / reasoning en décision explicable :

- confidence score
- evidence quality score
- uncertainty detection
- risk detection
- decision card
- human validation recommendation

## Fichiers à créer

Créer ces fichiers dans ton repository :

```text
talentcopilot/models/confidence.py
talentcopilot/models/risk.py
talentcopilot/models/uncertainty.py
talentcopilot/models/governance.py

talentcopilot/ai/evidence_quality_engine.py
talentcopilot/ai/confidence_engine.py
talentcopilot/ai/uncertainty_engine.py
talentcopilot/ai/risk_engine.py
talentcopilot/ai/explainability_engine.py
talentcopilot/ai/governance_engine.py

talentcopilot/ui/governance_cards.py

tests/test_governance_engine.py
tests/test_evidence_quality_engine.py
tests/test_risk_uncertainty_engine.py
```

## Commandes Colab

Depuis Colab, après avoir récupéré ton repository :

```bash
cd /content/talentcopilot-ai
```

Créer les dossiers si nécessaire :

```bash
mkdir -p talentcopilot/models
mkdir -p talentcopilot/ai
mkdir -p talentcopilot/ui
mkdir -p tests
```

Copier les fichiers du sprint dans les bons dossiers.

Puis lancer :

```bash
python -m pytest tests/test_governance_engine.py tests/test_evidence_quality_engine.py tests/test_risk_uncertainty_engine.py -q
```

Si tout passe :

```bash
git status
git add .
git commit -m "Mega Sprint 14 - Explainable AI Governance Layer"
git push
```

## Intégration Streamlit optionnelle

Dans ton espace candidat ou Decision Workspace, tu pourras ajouter :

```python
from talentcopilot.ai.governance_engine import GovernanceEngine
from talentcopilot.ui.governance_cards import render_governance_card

governance = GovernanceEngine().assess_candidate(candidate, job, reasoning_report)
render_governance_card(governance)
```

## Résultat attendu

Le système pourra produire une carte de décision :

```text
Decision: Strong Hire
Confidence: 91
Evidence Quality: 88
Risk Level: Low
Human Validation: Recommended
```

## Note importante

Cette livraison est volontairement non destructive : elle ajoute une nouvelle couche au lieu de remplacer les moteurs existants.
