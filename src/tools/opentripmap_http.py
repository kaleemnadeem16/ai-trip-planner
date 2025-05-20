from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urlencode

from src.utils.http_client import HttpClient, HTTPError


@dataclass
class OpenTripMapHttpClient:
    base_url: str = "https://api.opentripmap.com/0.1/en/places"
    api_key: Optional[str] = None
    user_agent: str = "mini-task-planner/0.1"
    default_radius: int = 3000
    client: HttpClient = field(default_factory=HttpClient)

    def radius_search(self, lat: float, lon: float, radius_m: Optional[int] = None, kinds: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        if self.api_key is None or self.api_key == "":
            raise HTTPError(401, "OpenTripMap API key required")
        r = radius_m or self.default_radius
        params = {
            "apikey": self.api_key,
            "radius": int(r),
            "lon": float(lon),
            "lat": float(lat),
            "limit": int(limit),
        }
        if kinds:
            params["kinds"] = kinds
        url = f"{self.base_url}/radius?{urlencode(params)}"
        self.client.user_agent = self.user_agent or self.client.user_agent
        data = self.client.get_json(url)
        if isinstance(data, dict):
            features = data.get("features")
            if isinstance(features, list):
                out = []
                for f in features:
                    props = f.get("properties", {}) if isinstance(f, dict) else {}
                    # Basic fields: name, kinds, lat/lon from geometry
                    name = props.get("name")
                    kinds_val = props.get("kinds")
                    geom = f.get("geometry", {}) if isinstance(f, dict) else {}
                    coords = geom.get("coordinates") if isinstance(geom, dict) else None
                    if isinstance(coords, list) and len(coords) >= 2:
                        lon2, lat2 = coords[0], coords[1]
                        out.append({
                            "name": name,
                            "kinds": kinds_val,
                            "lat": lat2,
                            "lon": lon2,
                        })
                return out
        return []
