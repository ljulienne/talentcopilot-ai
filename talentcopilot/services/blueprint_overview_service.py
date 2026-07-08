from talentcopilot.models.blueprint_overview import BlueprintLayer, BlueprintOverview, BlueprintPrinciple


class BlueprintOverviewService:
    def build(self) -> BlueprintOverview:
        return BlueprintOverview(
            title="TalentCopilot Enterprise Blueprint",
            positioning=(
                "TalentCopilot is an AI Hiring Decision Platform designed to make recruitment decisions "
                "more explainable, collaborative, evidence-based and auditable."
            ),
            principles=[
                BlueprintPrinciple("AI assists, humans decide", "Recommendations support human decision-making."),
                BlueprintPrinciple("No score without evidence", "Every score must be grounded in candidate evidence."),
                BlueprintPrinciple("No recommendation without confidence", "Recommendations must include certainty level."),
                BlueprintPrinciple("Fit and feasibility are separate", "Budget does not modify candidate fit."),
                BlueprintPrinciple("Every decision is traceable", "Decision Trace supports audit and trust."),
            ],
            layers=[
                BlueprintLayer("Product Blueprint", "Defines vision, principles, domain model and rules."),
                BlueprintLayer("Decision Intelligence Core", "Calculates evidence, fit, risk, budget, confidence and recommendations."),
                BlueprintLayer("Enterprise Workspaces", "Display intelligence outputs and support human decision-making."),
            ],
            next_chapters=[
                "Domain Model",
                "CandidateDecisionProfile",
                "Evidence Intelligence",
                "Fit Intelligence",
                "Risk Intelligence",
                "Budget Intelligence",
                "Recommendation Framework",
                "Decision Trace",
            ],
        )
