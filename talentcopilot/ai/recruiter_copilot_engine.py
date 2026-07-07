from typing import Any, List

from talentcopilot.models.recruiter_copilot import (
    CopilotAction,
    CopilotActionType,
    CopilotAlert,
    CopilotPriority,
    CopilotQuestion,
    RecruiterCopilotReport,
)


class RecruiterCopilotEngine:
    """
    Turns a DecisionReport into practical recruiter guidance.

    This layer is intentionally deterministic. It can later be enhanced with LLM
    generation, but the core recommendations remain explainable and testable.
    """

    def advise(self, candidate: Any, job: Any, decision_report: Any) -> RecruiterCopilotReport:
        candidate_name = self._candidate_name(candidate, decision_report)
        role_title = self._role_title(job, decision_report)
        recommendation = self._value(self._get(decision_report, "recommendation", "Review Carefully"))
        decision_score = self._get(decision_report, "decision_score", 0)
        confidence = self._value(self._get(decision_report, "confidence", "Medium"))
        human_validation = self._value(self._get(decision_report, "human_validation", "Recommended"))

        actions = self._build_actions(recommendation, decision_score, confidence, human_validation)
        alerts = self._build_alerts(decision_report, human_validation)
        questions = self._build_questions(decision_report)
        headline = self._headline(recommendation, decision_score)
        recruiter_summary = self._recruiter_summary(candidate_name, role_title, recommendation, decision_score, confidence, alerts)
        stakeholder_summary = self._stakeholder_summary(candidate_name, role_title, recommendation, decision_score, confidence)
        closing_recommendation = self._closing_recommendation(recommendation, alerts)

        return RecruiterCopilotReport(
            candidate_name=candidate_name,
            role_title=role_title,
            headline=headline,
            recruiter_summary=recruiter_summary,
            actions=actions,
            interview_questions=questions,
            alerts=alerts,
            stakeholder_summary=stakeholder_summary,
            closing_recommendation=closing_recommendation,
        )

    def _build_actions(self, recommendation: str, decision_score: float, confidence: str, human_validation: str) -> List[CopilotAction]:
        actions: List[CopilotAction] = []

        if recommendation == "Strong Hire":
            actions.append(CopilotAction(
                action_type=CopilotActionType.MOVE_FORWARD,
                priority=CopilotPriority.HIGH,
                title="Move candidate to the next stage",
                rationale="The consolidated decision recommendation is very positive.",
            ))
        elif recommendation == "Hire / Continue Process":
            actions.append(CopilotAction(
                action_type=CopilotActionType.MOVE_FORWARD,
                priority=CopilotPriority.HIGH,
                title="Continue the hiring process",
                rationale="The candidate appears aligned, but key assumptions should still be validated.",
            ))
        elif recommendation == "Review Carefully":
            actions.append(CopilotAction(
                action_type=CopilotActionType.VALIDATE,
                priority=CopilotPriority.HIGH,
                title="Run a structured recruiter review",
                rationale="The decision score is moderate and requires validation before progressing.",
            ))
        elif recommendation == "Hold":
            actions.append(CopilotAction(
                action_type=CopilotActionType.HOLD,
                priority=CopilotPriority.MEDIUM,
                title="Keep candidate in reserve",
                rationale="The candidate may be useful if stronger profiles are unavailable.",
            ))
        else:
            actions.append(CopilotAction(
                action_type=CopilotActionType.REJECT,
                priority=CopilotPriority.HIGH,
                title="Do not progress at this stage",
                rationale="The decision signals are not strong enough to recommend continuation.",
            ))

        if human_validation in {"Recommended", "Strongly Recommended"}:
            actions.append(CopilotAction(
                action_type=CopilotActionType.VALIDATE,
                priority=CopilotPriority.HIGH if human_validation == "Strongly Recommended" else CopilotPriority.MEDIUM,
                title="Validate AI recommendation with a human recruiter",
                rationale=f"Human validation level is {human_validation}.",
            ))

        if confidence == "Low":
            actions.append(CopilotAction(
                action_type=CopilotActionType.COMPARE,
                priority=CopilotPriority.MEDIUM,
                title="Compare against alternative candidates",
                rationale="The AI confidence is low, so comparison is recommended before deciding.",
            ))

        return actions

    def _build_alerts(self, decision_report: Any, human_validation: str) -> List[CopilotAlert]:
        alerts: List[CopilotAlert] = []

        for concern in self._as_list(self._get(decision_report, "concerns")):
            severity = self._priority(self._get(concern, "severity", "Medium"))
            alerts.append(CopilotAlert(
                severity=severity,
                title=str(self._get(concern, "title", "Concern")),
                message=str(self._get(concern, "explanation", "A concern requires validation.")),
                mitigation=str(self._get(concern, "mitigation", "Validate during interview.")),
            ))

        missing = self._as_list(self._get(decision_report, "missing_information"))
        if missing:
            alerts.append(CopilotAlert(
                severity=CopilotPriority.MEDIUM,
                title="Missing information",
                message=f"{len(missing)} missing information item(s) should be checked.",
                mitigation="Request clarification from the candidate or validate during interview.",
            ))

        if human_validation == "Strongly Recommended":
            alerts.append(CopilotAlert(
                severity=CopilotPriority.HIGH,
                title="Strong human validation required",
                message="The AI recommendation should not be used without recruiter validation.",
                mitigation="Review evidence, risks and interview focus before making a decision.",
            ))

        return alerts[:8]

    def _build_questions(self, decision_report: Any) -> List[CopilotQuestion]:
        questions: List[CopilotQuestion] = []

        focus_items = self._as_list(self._get(decision_report, "interview_focus"))
        concerns = self._as_list(self._get(decision_report, "concerns"))

        for item in focus_items[:5]:
            text = str(item)
            questions.append(CopilotQuestion(
                competency="Interview focus",
                question=self._question_from_focus(text),
                purpose=text,
                positive_signal="Candidate gives a specific, recent and measurable example.",
                red_flag="Candidate remains vague or cannot explain their own contribution.",
            ))

        for concern in concerns[:5]:
            title = str(self._get(concern, "title", "Concern"))
            mitigation = str(self._get(concern, "mitigation", "Validate this point during interview."))
            questions.append(CopilotQuestion(
                competency=title,
                question=f"Can you describe a concrete example that demonstrates {title}?",
                purpose=mitigation,
                positive_signal="Clear ownership, context, actions and measurable outcome.",
                red_flag="No concrete example or inconsistent explanation.",
            ))

        if not questions:
            questions.append(CopilotQuestion(
                competency="Role fit",
                question="Can you walk me through the most relevant project you have delivered for this role?",
                purpose="Validate role fit and evidence depth.",
                positive_signal="Structured answer with context, actions, impact and lessons learned.",
                red_flag="Generic answer with no clear personal contribution.",
            ))

        return questions[:8]

    def _question_from_focus(self, focus: str) -> str:
        focus = focus.strip().rstrip(".")
        if focus.lower().startswith("validate"):
            return f"Can you provide a concrete example to {focus[0].lower() + focus[1:]}?"
        return f"Can you provide a concrete example related to: {focus}?"

    def _headline(self, recommendation: str, decision_score: float) -> str:
        return f"{recommendation} — Decision score {round(float(decision_score), 1)}/100"

    def _recruiter_summary(self, candidate_name: str, role_title: str, recommendation: str, decision_score: float, confidence: str, alerts: List[CopilotAlert]) -> str:
        alert_text = f"{len(alerts)} alert(s) require attention" if alerts else "no major alert detected"
        return (
            f"{candidate_name} is assessed for {role_title}. Recommendation: {recommendation}. "
            f"Decision score: {round(float(decision_score), 1)}/100. Confidence: {confidence}. "
            f"There are {alert_text}."
        )

    def _stakeholder_summary(self, candidate_name: str, role_title: str, recommendation: str, decision_score: float, confidence: str) -> str:
        return (
            f"For {role_title}, TalentCopilot recommends: {recommendation} for {candidate_name}. "
            f"The decision score is {round(float(decision_score), 1)}/100 with {confidence.lower()} confidence."
        )

    def _closing_recommendation(self, recommendation: str, alerts: List[CopilotAlert]) -> str:
        if any(alert.severity == CopilotPriority.HIGH for alert in alerts):
            return "Proceed only after validating high-priority alerts."
        if recommendation in {"Strong Hire", "Hire / Continue Process"}:
            return "Proceed to the next stage with targeted validation."
        if recommendation == "Review Carefully":
            return "Run a structured review before progressing."
        if recommendation == "Hold":
            return "Keep in reserve and compare against stronger profiles."
        return "Do not progress unless new evidence is provided."

    def _candidate_name(self, candidate: Any, decision_report: Any) -> str:
        return str(self._get(candidate, "name", self._get(decision_report, "candidate_name", "Candidate")))

    def _role_title(self, job: Any, decision_report: Any) -> str:
        return str(self._get(job, "title", self._get(decision_report, "role_title", "Role")))

    def _priority(self, value: Any) -> CopilotPriority:
        raw = self._value(value)
        if raw == "High":
            return CopilotPriority.HIGH
        if raw == "Low":
            return CopilotPriority.LOW
        return CopilotPriority.MEDIUM

    def _value(self, value: Any) -> str:
        return getattr(value, "value", str(value))

    def _get(self, obj: Any, key: str, default: Any = None) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return list(value)
        return [value]
