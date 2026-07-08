from talentcopilot.interview.models import InterviewPlan, InterviewSection


class InterviewPlanService:
    def build(self, validation_topics: list[str]) -> InterviewPlan:
        critical = validation_topics[:3] if validation_topics else ["Role fit", "Motivation", "Stakeholder management"]

        sections = [
            InterviewSection("Introduction", 5, "Set context and explain interview structure."),
            InterviewSection("Career overview", 10, "Understand candidate trajectory and motivations."),
        ]

        for topic in critical:
            sections.append(
                InterviewSection(
                    f"Validate {topic}",
                    12,
                    f"Collect concrete examples and evidence for {topic}.",
                )
            )

        sections.extend([
            InterviewSection("Scenario questions", 12, "Assess judgment in realistic role situations."),
            InterviewSection("Candidate questions", 8, "Evaluate motivation and clarify expectations."),
            InterviewSection("Wrap-up", 5, "Confirm next steps and availability."),
        ])

        return InterviewPlan(
            total_minutes=sum(section.duration_minutes for section in sections),
            sections=sections,
        )
