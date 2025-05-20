from src.agents.decomposer import TaskDecomposer
from src.orchestrator.schemas import TripRequest, Place, LegRequest, LegDates


def test_decomposer_defaults_duration_when_missing():
    req = TripRequest(
        origin=Place(query="NYC"),
        legs=[
            LegRequest(**{"from": {"query": "NYC"}}, **{"to": {"query": "BOS"}}, dates=LegDates())
        ],
    )
    d = TaskDecomposer()
    out = d.decompose(req)
    assert out.legs[0].dates.duration_days == 2


def test_decomposer_sets_detect_origin_placeholder():
    req = TripRequest(
        origin=None,
        detect_origin=True,
        legs=[
            LegRequest(**{"from": {"query": "NYC"}}, **{"to": {"query": "BOS"}}, dates=LegDates(duration_days=1))
        ],
    )
    out = TaskDecomposer().decompose(req)
    assert out.origin is not None
    assert out.origin.query == "__detect_ip__"
