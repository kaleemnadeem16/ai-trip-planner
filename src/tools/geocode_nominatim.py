from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

# No network calls in tests; this is a placeholder interface.


@dataclass
class NominatimClient:
    base_url: str = "https://nominatim.openstreetmap.org/search"
    user_agent: str = "mini-task-planner/0.1"
    timeout: int = 8

    def geocode(self, query: str) -> Optional[tuple[float, float]]:
        """Return (lat, lon) or None. Placeholder implementation."""
        if not query:
            return None
        # Fake deterministic mapping for tests: hash to lat/lon-ish
        h = abs(hash(query)) % 10000
        lat = (h % 18000) / 100 - 90
        lon = (h % 36000) / 100 - 180
        return (lat, lon)
