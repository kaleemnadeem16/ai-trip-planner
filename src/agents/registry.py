from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AgentInfo:
    name: str
    tier: str  # e.g., input, planning, enrichment, validation, scheduling
    role: str


def list_agents() -> List[AgentInfo]:
    return [
        AgentInfo(name="TaskDecomposer", tier="planning", role="Normalize TripRequest; set defaults"),
        AgentInfo(name="ActivitiesAgent", tier="enrichment", role="Fetch/suggest POIs via OpenTripMap"),
        AgentInfo(name="ValidatorAgent", tier="validation", role="Detect missing geocode/insufficient activities; trigger replan"),
        AgentInfo(name="SchedulerAgent", tier="scheduling", role="Build DayPlans with morning/afternoon segments"),
        # Future/placeholder tiers
        AgentInfo(name="BudgetAgent", tier="planning", role="Allocate budget across legs and activities (planned)"),
        AgentInfo(name="CalendarAgent", tier="planning", role="Align plans with calendar constraints (planned)"),
    ]
