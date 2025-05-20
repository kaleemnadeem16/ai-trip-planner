from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class WorldTimeApiClient:
    base_url: str = "https://worldtimeapi.org/api"
    timeout: int = 8

    def timezone_for_latlon(self, lat: float, lon: float) -> Optional[str]:
        # Placeholder: rough bucket by longitude
        if lon is None:
            return None
        if -90 <= lon < -60:
            return "America/New_York"
        if -60 <= lon < -30:
            return "America/Halifax"
        if -30 <= lon < 0:
            return "Atlantic/Azores"
        if 0 <= lon < 30:
            return "Europe/Paris"
        if 30 <= lon < 60:
            return "Europe/Moscow"
        return "UTC"
