from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExchangeRateClient:
    base_url: str = "https://api.exchangerate.host"
    timeout: int = 8

    def convert(self, amount: float, from_ccy: str, to_ccy: str) -> Optional[float]:
        # Placeholder: identity if same currency, else a simple static ratio
        if from_ccy == to_ccy:
            return amount
        # Fake: USD->EUR 0.9, EUR->USD 1.1; otherwise 1:1 for now
        pair = (from_ccy.upper(), to_ccy.upper())
        if pair == ("USD", "EUR"):
            return round(amount * 0.9, 2)
        if pair == ("EUR", "USD"):
            return round(amount * 1.1, 2)
        return round(amount, 2)
