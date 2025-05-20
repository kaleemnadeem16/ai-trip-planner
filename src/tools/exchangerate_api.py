from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlencode

from src.utils.http_client import HttpClient, HTTPError


@dataclass
class ExchangeRateAPI:
    base_url: str = "https://api.exchangerate.host"
    api_key: Optional[str] = None
    client: HttpClient = field(default_factory=HttpClient)

    def convert(self, amount: float, from_ccy: str, to_ccy: str) -> float:
        if from_ccy.upper() == to_ccy.upper():
            return round(amount, 2)
        params = {
            "from": from_ccy.upper(),
            "to": to_ccy.upper(),
            "amount": float(amount),
        }
        if self.api_key:
            params["access_key"] = self.api_key
        url = f"{self.base_url}/convert?{urlencode(params)}"
        data = self.client.get_json(url)
        # Prefer 'result' if present
        if isinstance(data, dict):
            if "result" in data and isinstance(data["result"], (int, float)):
                return round(float(data["result"]), 2)
            # Fallback: info.rate * amount
            info = data.get("info") if isinstance(data.get("info"), dict) else None
            if info and isinstance(info.get("rate"), (int, float)):
                return round(float(info["rate"]) * float(amount), 2)
        raise HTTPError(500, f"Unexpected response from exchangerate API: {data!r}")
