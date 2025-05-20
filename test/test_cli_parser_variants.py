from src.cli.parser import parse_instruction, ParseError
from src.orchestrator.schemas import TripRequest


def test_parse_variants_without_dates():
    req = parse_instruction("plan a trip from NYC to Boston")
    assert isinstance(req, TripRequest)
    assert req.legs[0].dates.fixed is None


def test_parse_reversed_phrase():
    req = parse_instruction("plan a trip to Boston from NYC on 2025-09-01 to 2025-09-02")
    assert req.legs[0].dates.fixed == ["2025-09-01", "2025-09-02"]
