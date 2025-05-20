from src.cli.parser import parse_instruction
from src.orchestrator.schemas import TripRequest


def test_parse_current_location():
    req = parse_instruction("from my current location to Boston on 2025-09-01 to 2025-09-02")
    assert isinstance(req, TripRequest)
    assert req.detect_origin is True
    assert req.origin.query == "__detect_ip__"
    assert req.legs[0].from_place.query == "__detect_ip__"
