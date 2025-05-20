from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple
from urllib.parse import urlencode

from src.utils.http_client import HttpClient


@dataclass
class NominatimHttpClient:
    base_url: str = "https://nominatim.openstreetmap.org/search"
    user_agent: str = "mini-task-planner/0.1"
    client: HttpClient = field(default_factory=HttpClient)

    def geocode(self, query: str) -> Optional[Tuple[float, float]]:
        if not query:
            return None
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
        }
        url = f"{self.base_url}?{urlencode(params)}"
        # Ensure UA header overrides default if provided on class
        self.client.user_agent = self.user_agent or self.client.user_agent
        data = self.client.get_json(url)
        if isinstance(data, list) and data:
            item = data[0]
            try:
                lat = float(item.get("lat"))
                lon = float(item.get("lon"))
                return (lat, lon)
            except (TypeError, ValueError):
                return None
        return None
