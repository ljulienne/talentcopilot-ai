"""Recruitment Mission workspace architecture introduced in Release 6.0A."""

from .state import CandidateMissionView, RecruitmentMissionState, build_recruitment_mission_state

__all__ = [
    "CandidateMissionView",
    "RecruitmentMissionState",
    "build_recruitment_mission_state",
]
