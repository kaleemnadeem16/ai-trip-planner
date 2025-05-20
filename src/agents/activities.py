from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.orchestrator.schemas import TripRequest
from src.agents.interest_mapping_agent import InterestMappingAgent


@dataclass
class ActivitiesAgent:
    limit_per_leg: int = 5
    
    def __post_init__(self):
        self.interest_mapper = InterestMappingAgent()

    def suggest_pois(self, request: TripRequest, context: Dict[str, Any], otm_client) -> List[Dict[str, Any]]:
        # Use geocoded destination of first leg for now
        geocodes = context.get("geocodes") if isinstance(context, dict) else None
        dest = geocodes.get("to") if isinstance(geocodes, dict) else None
        if not dest or "lat" not in dest or "lon" not in dest:
            return []

        lat, lon = dest["lat"], dest["lon"]

        # Use LLM-powered interest mapping instead of hardcoded dictionary
        interests = []
        if request.preferences and request.preferences.interests:
            interests = [s.strip() for s in request.preferences.interests if isinstance(s, str)]
        
        kinds = self.interest_mapper.map_interests_to_kinds(interests)

        items = otm_client.radius_search(lat=lat, lon=lon, kinds=kinds, limit=self.limit_per_leg)
        # Normalize to simple POI dicts
        out: List[Dict[str, Any]] = []
        for it in items:
            name = it.get("name")
            if not name:
                continue
            out.append({
                "name": name,
                "category": it.get("kinds"),
                "lat": it.get("lat"),
                "lon": it.get("lon"),
            })
        return out
