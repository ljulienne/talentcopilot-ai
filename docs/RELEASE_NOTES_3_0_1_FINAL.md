# TalentCopilot-AI — Release 3.0.1 Final

## Base Git

Correctif final appliqué sur le commit :

`62958082b332c219d76ee890a63189f5c1a257c8`

## Cause racine

La navigation « Candidate Intelligence » ouvrait encore :

`talentcopilot.ui.candidate_workspace_v2.render_candidate_workspace_v2`

Cette ancienne page utilisait `CandidateWorkspaceV2Service` et un
`CandidateDecisionProfile.fit_score` recalculé par le Decision Core.

Elle affichait donc 41 % pour David Smith alors que la session officielle
contenait environ 4,19 %.

## Correctif

La navigation ouvre désormais :

`talentcopilot.ui.candidate_workspace.render_candidate_workspace`

Cette page consomme exclusivement :

`RecruitmentSession.ranked_analyses`
→ `CandidateWorkspaceService`
→ `CandidateIntelligenceService`

## Règle architecturale

Candidate Intelligence ne calcule pas de second score de matching.

Le Mission Fit affiché doit toujours être égal à :

`CandidateAnalysisState.match_score`

et son classement doit toujours être égal à :

`CandidateAnalysisState.rank`

## Tests

Le test de non-régression vérifie :

- la route réelle de navigation ;
- le module et la fonction utilisés ;
- le score officiel de David Smith ;
- le rang officiel de David Smith ;
- la cohérence de tous les candidats ;
- l'absence de retour du score historique de 41 %.
