from __future__ import annotations

from src.agents.activities import ActivitiesAgent
from src.orchestrator.schemas import TripRequest, LegRequest, LegDates, Place, Preferences


def test_activities_agent_suggests_from_context_geocode():
    req = TripRequest(
        origin=Place(query="Boston"),
        legs=[LegRequest(**{"from": Place(query="Boston"), "to": Place(query="New York"), "dates": LegDates(duration_days=2)})],
        preferences=Preferences(interests=["museums", "parks"]) 
    )
    ctx = {"geocodes": {"to": {"lat": 40.7128, "lon": -74.0060}}}

    class FakeOTM:
        def radius_search(self, lat, lon, kinds=None, limit=5):
            assert kinds in (None, "museums,parks")
            return [
                {"name": "Museum A", "kinds": "museums", "lat": lat, "lon": lon},
                {"name": "Park B", "kinds": "parks", "lat": lat+0.01, "lon": lon+0.01},
            ]

    acts = ActivitiesAgent(limit_per_leg=2).suggest_pois(req, ctx, FakeOTM())
    assert len(acts) == 2
    assert acts[0]["name"] == "Museum A"


def test_orchestrator_enriches_with_activities(monkeypatch):
    # Patch get_settings to return fake otm key and radius
    from src.orchestrator.orchestrator import Orchestrator
    from src.orchestrator.blackboard import Blackboard
    from src.orchestrator.schemas import TripRequest, LegRequest, LegDates, Place

    class FakeSettings:
        class Tools:
            otm_api_key = "key"
            otm_default_radius = 1000
            nominatim_base_url = "https://nominatim.example.com"
            nominatim_user_agent = "test-agent"
            open_meteo_base_url = "https://meteo.example.com"
        tools = Tools()
    monkeypatch.setattr("src.orchestrator.orchestrator.get_settings", lambda: FakeSettings())

    # Patch NominatimClient and OpenMeteoClient to avoid randomness
    import src.orchestrator.orchestrator as orch_mod
    class FakeGeo:
        def geocode(self, q):
            if "New York" in q:
                return (40.7128, -74.0060)
            return (42.3601, -71.0589)
    class FakeWx:
        def forecast_summary(self, lat, lon):
            return {"summary": "Sunny", "temp_c": 22.0, "precip_prob": 0.1}
    class FakeOTM:
        def __init__(self, api_key, default_radius):
            self.default_radius = default_radius
        def radius_search(self, lat, lon, kinds=None, limit=5):
            # Return empty when radius small; one POI when larger to simulate replan behavior elsewhere
            return [{"name": "Poi", "kinds": "museums", "lat": lat, "lon": lon}]

    monkeypatch.setattr(orch_mod, "NominatimHttpClient", lambda *args, **kwargs: FakeGeo())
    monkeypatch.setattr(orch_mod, "OpenMeteoHttpClient", lambda *args, **kwargs: FakeWx())
    monkeypatch.setattr(orch_mod, "OpenTripMapHttpClient", lambda api_key, default_radius: FakeOTM(api_key, default_radius))

    orchestrator = Orchestrator(blackboard=Blackboard())
    req = TripRequest(
        origin=Place(query="Boston"),
        legs=[LegRequest(**{"from": Place(query="Boston"), "to": Place(query="New York"), "dates": LegDates(duration_days=2)})]
    )
    result = orchestrator.plan(req)
    acts = result["itinerary"]["artifacts"].get("activities")
    assert "to" in acts and len(acts["to"]) == 1


def test_orchestrator_replans_when_insufficient(monkeypatch):
    from src.orchestrator.orchestrator import Orchestrator
    from src.orchestrator.blackboard import Blackboard
    from src.orchestrator.schemas import TripRequest, LegRequest, LegDates, Place

    class FakeSettings:
        class Tools:
            otm_api_key = "key"
            otm_default_radius = 100  # small
            nominatim_base_url = "https://nominatim.example.com"
            nominatim_user_agent = "test-agent"
            open_meteo_base_url = "https://meteo.example.com"
        tools = Tools()
    monkeypatch.setattr("src.orchestrator.orchestrator.get_settings", lambda: FakeSettings())

    import src.orchestrator.orchestrator as orch_mod
    class FakeGeo:
        def geocode(self, q):
            return (40.7128, -74.0060)
    class FakeWx:
        def forecast_summary(self, lat, lon):
            return {"summary": "Sunny", "temp_c": 22.0, "precip_prob": 0.1}

    class FakeOTM:
        def __init__(self, api_key, default_radius):
            self.radius = default_radius
        def radius_search(self, lat, lon, kinds=None, limit=5):
            # First pass (small radius) -> empty, second pass -> one item
            if self.radius <= 100:
                # simulate first call
                self.radius = int(self.radius * 1.5)
                return []
            return [{"name": "Poi2", "kinds": "parks", "lat": lat, "lon": lon}]

    monkeypatch.setattr(orch_mod, "NominatimHttpClient", lambda *args, **kwargs: FakeGeo())
    monkeypatch.setattr(orch_mod, "OpenMeteoHttpClient", lambda *args, **kwargs: FakeWx())
    monkeypatch.setattr(orch_mod, "OpenTripMapHttpClient", lambda api_key, default_radius: FakeOTM(api_key, default_radius))

    orchestrator = Orchestrator(blackboard=Blackboard())
    req = TripRequest(
        origin=Place(query="A"),
        legs=[LegRequest(**{"from": Place(query="A"), "to": Place(query="B"), "dates": LegDates(duration_days=1)})]
    )
    result = orchestrator.plan(req)
    acts = result["itinerary"]["artifacts"].get("activities")
    assert len(acts.get("to", [])) == 1
