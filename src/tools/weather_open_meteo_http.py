from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from urllib.parse import urlencode

from src.utils.http_client import HttpClient


@dataclass
class OpenMeteoHttpClient:
    base_url: str = "https://api.open-meteo.com/v1/forecast"
    user_agent: str = "mini-task-planner/0.1"
    client: HttpClient = field(default_factory=HttpClient)

    def forecast_summary(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        if lat is None or lon is None:
            return None
        params = {
            "latitude": float(lat),
            "longitude": float(lon),
            "current_weather": True,
            "hourly": "temperature_2m,precipitation_probability",
        }
        url = f"{self.base_url}?{urlencode(params)}"
        self.client.user_agent = self.user_agent or self.client.user_agent
        data = self.client.get_json(url)
        # Prefer current_weather with precipitation from hourly
        if isinstance(data, dict):
            cw = data.get("current_weather")
            hourly = data.get("hourly")
            
            if isinstance(cw, dict) and "temperature" in cw:
                precip_prob = 0.0  # default
                # Get precipitation probability from first hourly value
                if isinstance(hourly, dict):
                    precip_probs = hourly.get("precipitation_probability")
                    if isinstance(precip_probs, list) and precip_probs:
                        precip_prob = float(precip_probs[0]) / 100.0  # Convert percentage to decimal
                
                return {
                    "summary": "Current weather",
                    "temp_c": float(cw.get("temperature")),
                    "precip_prob": precip_prob
                }
            
            # Fallback to first hourly temperature if present
            if isinstance(hourly, dict):
                temps = hourly.get("temperature_2m")
                precip_probs = hourly.get("precipitation_probability")
                if isinstance(temps, list) and temps:
                    precip_prob = 0.0
                    if isinstance(precip_probs, list) and precip_probs:
                        precip_prob = float(precip_probs[0]) / 100.0
                    return {
                        "summary": "Hourly temperature", 
                        "temp_c": float(temps[0]),
                        "precip_prob": precip_prob
                    }
        return None
