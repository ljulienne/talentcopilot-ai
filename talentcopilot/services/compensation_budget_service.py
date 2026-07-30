from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from talentcopilot.models.hiring_budget import HiringBudgetInput


@dataclass(frozen=True)
class CandidateCompensationExpectation:
    candidate_id: str
    candidate_name: str
    currency: str = "EUR"
    expected_salary: float = 0.0
    variable_compensation: float = 0.0
    benefits_value: float = 0.0
    benefits_requested: str = ""
    relocation_support_requested: float = 0.0
    signing_bonus_requested: float = 0.0
    notice_period_weeks: int = 0
    availability_date: str = ""
    visa_sponsorship_required: bool = False
    flexibility: str = "Unknown"
    notes: str = ""
    updated_by: str = "Recruiter"
    updated_at: str = ""

    @property
    def documented(self) -> bool:
        return bool(
            self.expected_salary
            or self.variable_compensation
            or self.benefits_requested.strip()
            or self.relocation_support_requested
            or self.signing_bonus_requested
            or self.notice_period_weeks
            or self.availability_date.strip()
            or self.notes.strip()
        )

    @property
    def requested_package(self) -> float:
        return float(
            self.expected_salary
            + self.variable_compensation
            + self.benefits_value
            + self.relocation_support_requested
            + self.signing_bonus_requested
        )


@dataclass(frozen=True)
class OfferScenario:
    label: str
    base_salary: float
    variable_compensation: float
    benefits_value: float
    signing_bonus: float
    relocation_support: float
    first_year_cost: float
    position: str
    rationale: str


class CompensationBudgetService:
    """Persist recruiter-entered budget and candidate expectations on the session.

    Compensation signals are deliberately kept separate from official talent scores,
    ranks and recommendations. The service only reads and writes ``session.metadata``.
    """

    BUDGET_KEY = "compensation_budget"
    CANDIDATE_KEY = "candidate_compensation"
    AUDIT_KEY = "compensation_audit_log"

    def default_budget(self) -> HiringBudgetInput:
        return HiringBudgetInput(
            target_salary=85000.0,
            maximum_salary=100000.0,
            minimum_salary=70000.0,
            currency="EUR",
            target_bonus_percent=10.0,
            benefits_budget=6000.0,
            relocation_budget=8000.0,
            agency_fee=0.0,
            signing_bonus=5000.0,
            onboarding_cost=4000.0,
            first_year_cost_limit=120000.0,
        )

    @staticmethod
    def _metadata(session: Any) -> dict[str, Any]:
        if session is None:
            return {}
        metadata = getattr(session, "metadata", None)
        if not isinstance(metadata, dict):
            metadata = {}
            setattr(session, "metadata", metadata)
        return metadata

    @staticmethod
    def candidate_key(candidate_id: str = "", candidate_name: str = "") -> str:
        return str(candidate_id or candidate_name or "candidate").strip()

    def load_budget(self, session: Any) -> HiringBudgetInput:
        default = self.default_budget()
        raw = self._metadata(session).get(self.BUDGET_KEY, {})
        if not isinstance(raw, Mapping):
            return default
        values = asdict(default)
        for key in values:
            if key in raw:
                values[key] = raw[key]
        try:
            return HiringBudgetInput(**values)
        except (TypeError, ValueError):
            return default

    def save_budget(
        self,
        session: Any,
        budget: HiringBudgetInput,
        *,
        actor: str = "Recruiter",
    ) -> HiringBudgetInput:
        metadata = self._metadata(session)
        metadata[self.BUDGET_KEY] = asdict(budget)
        self._audit(metadata, actor, "position_budget_updated", "Position compensation framework updated")
        self._mark_updated(session)
        self._persist(session)
        return budget

    def load_expectation(
        self,
        session: Any,
        *,
        candidate_id: str = "",
        candidate_name: str = "",
    ) -> CandidateCompensationExpectation:
        key = self.candidate_key(candidate_id, candidate_name)
        raw_store = self._metadata(session).get(self.CANDIDATE_KEY, {})
        raw = raw_store.get(key, {}) if isinstance(raw_store, Mapping) else {}
        if not isinstance(raw, Mapping):
            raw = {}
        values = {
            "candidate_id": str(raw.get("candidate_id", candidate_id) or candidate_id),
            "candidate_name": str(raw.get("candidate_name", candidate_name) or candidate_name or "Candidate"),
            "currency": str(raw.get("currency", "EUR") or "EUR"),
            "expected_salary": self._number(raw.get("expected_salary")),
            "variable_compensation": self._number(raw.get("variable_compensation")),
            "benefits_value": self._number(raw.get("benefits_value")),
            "benefits_requested": str(raw.get("benefits_requested", "") or ""),
            "relocation_support_requested": self._number(raw.get("relocation_support_requested")),
            "signing_bonus_requested": self._number(raw.get("signing_bonus_requested")),
            "notice_period_weeks": int(self._number(raw.get("notice_period_weeks"))),
            "availability_date": str(raw.get("availability_date", "") or ""),
            "visa_sponsorship_required": bool(raw.get("visa_sponsorship_required", False)),
            "flexibility": str(raw.get("flexibility", "Unknown") or "Unknown"),
            "notes": str(raw.get("notes", "") or ""),
            "updated_by": str(raw.get("updated_by", "Recruiter") or "Recruiter"),
            "updated_at": str(raw.get("updated_at", "") or ""),
        }
        return CandidateCompensationExpectation(**values)

    def save_expectation(
        self,
        session: Any,
        expectation: CandidateCompensationExpectation,
        *,
        actor: str = "Recruiter",
    ) -> CandidateCompensationExpectation:
        metadata = self._metadata(session)
        store = metadata.setdefault(self.CANDIDATE_KEY, {})
        if not isinstance(store, dict):
            store = {}
            metadata[self.CANDIDATE_KEY] = store
        now = datetime.now(timezone.utc).isoformat()
        saved = CandidateCompensationExpectation(
            **{
                **asdict(expectation),
                "updated_by": actor,
                "updated_at": now,
            }
        )
        key = self.candidate_key(saved.candidate_id, saved.candidate_name)
        store[key] = asdict(saved)
        self._audit(metadata, actor, "candidate_expectation_updated", saved.candidate_name)
        self._mark_updated(session)
        self._persist(session)
        return saved

    def all_expectations(self, session: Any) -> tuple[CandidateCompensationExpectation, ...]:
        values = []
        analyses = list(getattr(session, "ranked_analyses", []) or []) if session is not None else []
        for analysis in analyses:
            values.append(
                self.load_expectation(
                    session,
                    candidate_id=str(getattr(analysis, "candidate_id", "") or ""),
                    candidate_name=str(getattr(analysis, "candidate_name", "Candidate") or "Candidate"),
                )
            )
        return tuple(values)

    def documented_count(self, session: Any) -> int:
        return sum(1 for item in self.all_expectations(session) if item.documented)

    def offer_scenarios(
        self,
        budget: HiringBudgetInput,
        expectation: CandidateCompensationExpectation,
    ) -> tuple[OfferScenario, ...]:
        target_bonus = max(0.0, budget.target_salary * budget.target_bonus_percent / 100.0)
        requested_bonus = max(0.0, expectation.variable_compensation)
        requested_benefits = max(0.0, expectation.benefits_value)
        requested_signing = max(0.0, expectation.signing_bonus_requested)
        requested_relocation = max(0.0, expectation.relocation_support_requested)

        scenarios = [
            self._scenario(
                "Budget-aligned",
                budget.target_salary,
                target_bonus,
                budget.benefits_budget,
                min(budget.signing_bonus, requested_signing),
                min(budget.relocation_budget, requested_relocation),
                budget,
                "Keeps the offer close to the approved target package.",
            ),
            self._scenario(
                "Balanced negotiation",
                min(
                    budget.maximum_salary,
                    max(budget.target_salary, expectation.expected_salary or budget.target_salary),
                ),
                min(max(target_bonus, requested_bonus), max(target_bonus, requested_bonus)),
                max(budget.benefits_budget, requested_benefits),
                min(max(budget.signing_bonus, requested_signing), requested_signing or budget.signing_bonus),
                min(max(budget.relocation_budget, requested_relocation), requested_relocation or budget.relocation_budget),
                budget,
                "Balances the candidate request with the approved salary ceiling and benefits levers.",
            ),
        ]
        if expectation.documented:
            scenarios.append(
                self._scenario(
                    "Candidate-requested",
                    expectation.expected_salary or budget.target_salary,
                    requested_bonus,
                    requested_benefits,
                    requested_signing,
                    requested_relocation,
                    budget,
                    "Reflects the currently documented candidate request for negotiation planning.",
                )
            )
        return tuple(scenarios)

    @staticmethod
    def _scenario(
        label: str,
        base_salary: float,
        variable: float,
        benefits: float,
        signing: float,
        relocation: float,
        budget: HiringBudgetInput,
        rationale: str,
    ) -> OfferScenario:
        total = float(
            base_salary
            + variable
            + benefits
            + signing
            + relocation
            + budget.agency_fee
            + budget.onboarding_cost
        )
        limit = float(budget.first_year_cost_limit or 0.0)
        if limit <= 0:
            limit = float(
                budget.maximum_salary
                + budget.benefits_budget
                + budget.signing_bonus
                + budget.relocation_budget
                + budget.agency_fee
                + budget.onboarding_cost
            )
        position = "Within range" if total <= limit else "Above range"
        return OfferScenario(
            label=label,
            base_salary=float(base_salary),
            variable_compensation=float(variable),
            benefits_value=float(benefits),
            signing_bonus=float(signing),
            relocation_support=float(relocation),
            first_year_cost=total,
            position=position,
            rationale=rationale,
        )

    @staticmethod
    def _number(value: Any) -> float:
        try:
            return max(0.0, float(value or 0.0))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _mark_updated(session: Any) -> None:
        if session is not None and hasattr(session, "mark_updated"):
            session.mark_updated()

    @staticmethod
    def _persist(session: Any) -> None:
        try:
            from talentcopilot.services.recruitment_project_persistence import persist_project_best_effort

            persist_project_best_effort(session)
        except Exception:
            pass

    @staticmethod
    def _audit(metadata: dict[str, Any], actor: str, event: str, detail: str) -> None:
        entries = metadata.setdefault(CompensationBudgetService.AUDIT_KEY, [])
        if not isinstance(entries, list):
            entries = []
            metadata[CompensationBudgetService.AUDIT_KEY] = entries
        entries.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": str(actor or "Recruiter"),
                "event": event,
                "detail": detail,
            }
        )
