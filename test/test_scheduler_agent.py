import json
from datetime import datetime

from src.agents.scheduler import SchedulerAgent
from src.orchestrator.blackboard import Blackboard
from src.orchestrator.orchestrator import Orchestrator
from src.orchestrator.schemas import TripRequest, Place, LegRequest, LegDates, DayPlan


def test_scheduler_basic_two_days():
    req = TripRequest(
        origin=Place(query="NYC"),
        legs=[
            LegRequest(
                **{"from": {"query": "NYC"}},
                **{"to": {"query": "Boston"}},
                dates=LegDates(fixed=["2025-09-01", "2025-09-03"]),
            )
        ],
    )
    ctx = {"activities": {"to": [{"name": "Museum"}, {"name": "Park"}, {"name": "Aquarium"}]} }
    days = SchedulerAgent().schedule(req, ctx)
    assert len(days) == 2
    for d in days:
        assert len(d.segments) == 2
        assert d.segments[0].start.endswith("T09:00:00")
        assert d.segments[1].start.endswith("T13:00:00")


def test_orchestrator_produces_days_when_dates():
    bb = Blackboard()
    orch = Orchestrator(blackboard=bb)
    req = TripRequest(
        origin=Place(query="New York"),
        legs=[
            LegRequest(
                **{"from": {"query": "New York"}},
                **{"to": {"query": "Boston"}},
                dates=LegDates(fixed=["2025-09-01", "2025-09-02"]),
            )
        ],
    )
    out = orch.plan(req)
    days = out["itinerary"]["days"]
    assert isinstance(days, list)
    assert len(days) == 1
    assert len(days[0]["segments"]) == 2
