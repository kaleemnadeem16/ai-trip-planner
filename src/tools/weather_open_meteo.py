from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenMeteoClient:
    base_url: str = "https://api.open-meteo.com/v1/forecast"
    timeout: int = 8

    def forecast_summary(self, lat: float, lon: float) -> Optional[dict]:
        """Return a minimal summary dict; placeholder logic for tests."""
        if lat is None or lon is None:
            return None
        # Fake mapping: temp varies with latitude; precip with lon parity
        temp_c = 30 - abs(lat) * 0.2
        precip_prob = 0.7 if int(abs(lon)) % 2 == 0 else 0.3
        return {"summary": "Partly cloudy", "temp_c": round(temp_c, 1), "precip_prob": precip_prob}
