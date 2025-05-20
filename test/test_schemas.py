from pydantic import ValidationError
from src.orchestrator.schemas import TripRequest, LegRequest, Place, LegDates


def test_trip_request_minimal_fixed_dates():
    req = TripRequest(
        detect_origin=True,
        legs=[
            LegRequest(
                **{
                    "from": {"query": "Lahore"},
                    "to": {"query": "New York"},
                    "dates": {"fixed": ["2025-09-10", "2025-09-12"]},
                }
            )
        ],
    )
    assert req.legs[0].to_place.query == "New York"


def test_leg_dates_fixed_requires_two():
    try:
        LegDates(fixed=["2025-09-10"])  # wrong length
        assert False, "Expected ValidationError"
    except ValidationError:
        pass
