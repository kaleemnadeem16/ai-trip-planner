from src.cli.parser import parse_instruction
from src.agents.activities import ActivitiesAgent, INTEREST_TO_KINDS
from src.orchestrator.schemas import TripRequest


def test_interests_in_cli():
    # Test that CLI instruction parsing preserves pace but doesn't set interests
    req = parse_instruction("plan a relaxed trip from NYC to Boston")
    assert req.preferences.pace == "easy"
    assert req.preferences.interests is None  # interests come from CLI flag, not instruction text


def test_activities_agent_uses_interests():
    from src.orchestrator.schemas import Preferences, Place
    req = TripRequest(
        origin=Place(query="NYC"),
        legs=[],
        preferences=Preferences(interests=["museums", "food"])
    )
    
    # Mock context with destination geocode
    context = {
        "geocodes": {
            "to": {"lat": 42.3601, "lon": -71.0589}
        }
    }
    
    # Mock OTM client
    class MockOTMClient:
        def radius_search(self, lat, lon, kinds=None, limit=5):
            # Should be called with kinds="catering,museums" based on interests mapping
            assert kinds is not None
            assert "museums" in kinds
            assert "catering" in kinds
            return [{"name": "Test Museum", "kinds": "museums", "lat": lat, "lon": lon}]
    
    agent = ActivitiesAgent()
    results = agent.suggest_pois(req, context, MockOTMClient())
    assert len(results) == 1
    assert results[0]["name"] == "Test Museum"


def test_interest_mapping():
    # Verify our interest to kinds mapping works
    assert INTEREST_TO_KINDS["museums"] == "museums"
    assert INTEREST_TO_KINDS["food"] == "catering"
    assert INTEREST_TO_KINDS["parks"] == "parks"
