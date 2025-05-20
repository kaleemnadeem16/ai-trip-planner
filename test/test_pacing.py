from src.cli.parser import parse_instruction
from src.agents.scheduler import SchedulerAgent
from src.orchestrator.schemas import TripRequest


def test_parse_instruction_with_pace():
    req = parse_instruction("plan a relaxed trip from NYC to Boston on 2025-09-01 to 2025-09-02")
    assert req.preferences.pace == "easy"

def test_scheduler_respects_pace():
    req = TripRequest(
        origin=None,
        legs=[],
        preferences={"pace": "packed"}
    )
    # Mock context and dates for scheduler test
    import datetime
    from src.orchestrator.schemas import Place, LegRequest, LegDates
    req.legs = [LegRequest(
        **{"from": {"query": "NYC"}},
        **{"to": {"query": "Boston"}}, 
        dates=LegDates(fixed=["2025-09-01", "2025-09-02"])
    )]
    
    days = SchedulerAgent().schedule(req, {})
    assert len(days) == 1
    assert len(days[0].segments) == 3  # packed = 3 segments
