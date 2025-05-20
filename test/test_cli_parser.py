from src.cli.parser import parse_instruction, ParseError
from src.orchestrator.schemas import TripRequest


def test_parse_instruction_happy():
    req = parse_instruction("from NYC to Boston on 2025-09-01 to 2025-09-03")
    assert isinstance(req, TripRequest)
    assert req.origin.query.lower() == "nyc"
    assert req.legs[0].to_place.query.lower() == "boston"
    assert req.legs[0].dates.fixed == ["2025-09-01", "2025-09-03"]


def test_parse_instruction_error():
    try:
        parse_instruction("fly to the moon")
        assert False, "Expected ParseError"
    except ParseError:
        pass
