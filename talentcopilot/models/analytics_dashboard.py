from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalyticsKPI:
    label: str
    value: str
    delta: str = ""


@dataclass
class AnalyticsSignal:
    area: str
    score: int
    status: str
    detail: str


@dataclass
class AnalyticsFunnelStage:
    name: str
    count: int
    conversion: int


@dataclass
class AnalyticsDashboardReport:
    role_title: str
    session_id: str
    global_readiness: int
    kpis: List[AnalyticsKPI] = field(default_factory=list)
    signals: List[AnalyticsSignal] = field(default_factory=list)
    funnel: List[AnalyticsFunnelStage] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
