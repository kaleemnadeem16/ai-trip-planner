from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple
from urllib.parse import quote

from src.utils.http_client import HttpClient


@dataclass
class OSRMHttpClient:
    base_url: str = "https://router.project-osrm.org"
    profile: str = "driving"
    user_agent: str = "mini-task-planner/0.1"
    client: HttpClient = field(default_factory=HttpClient)

    def route_distance_km(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[float]:
        if start is None or end is None:
            return None
        slat, slon = float(start[0]), float(start[1])
        elat, elon = float(end[0]), float(end[1])
        # OSRM expects lon,lat order
        coords = f"{slon},{slat};{elon},{elat}"
        url = f"{self.base_url}/route/v1/{quote(self.profile)}/{coords}?overview=false&alternatives=false&steps=false"
        self.client.user_agent = self.user_agent or self.client.user_agent
        data = self.client.get_json(url)
        if isinstance(data, dict) and isinstance(data.get("routes"), list) and data["routes"]:
            route = data["routes"][0]
            dist_m = route.get("distance")
            if isinstance(dist_m, (int, float)):
                return round(float(dist_m) / 1000.0, 2)
        return None
