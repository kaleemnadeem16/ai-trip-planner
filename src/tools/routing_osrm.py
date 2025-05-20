from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class OSRMClient:
    base_url: str = "https://router.project-osrm.org"
    profile: str = "driving"
    timeout: int = 8

    def route_distance_km(self, a: Tuple[float, float], b: Tuple[float, float]) -> Optional[float]:
        # Placeholder: great-circle-ish rough metric using Manhattan distance
        if not a or not b:
            return None
        lat1, lon1 = a
        lat2, lon2 = b
        return round((abs(lat1 - lat2) * 111) + (abs(lon1 - lon2) * 85), 1)
