from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from src.tools.weather_open_meteo_http import OpenMeteoHttpClient
from src.utils.http_client import HttpClient, RetryPolicy


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method: str, url: str, headers: Dict[str, str], body: Optional[bytes], timeout: int) -> Tuple[int, Dict[str, str], bytes]:
        self.calls.append((method, url, headers, body, timeout))
        status, hdrs, body_bytes = self.responses.pop(0)
        return status, hdrs, body_bytes


def no_sleep(_):
    pass


def test_open_meteo_current_weather_success():
    payload = {"current_weather": {"temperature": 22.5}}
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    om = OpenMeteoHttpClient(client=client)
    s = om.forecast_summary(42.36, -71.06)
    assert s == {"summary": "Current weather", "temp_c": 22.5, "precip_prob": 0.0}


def test_open_meteo_hourly_fallback():
    payload = {"hourly": {"temperature_2m": [19.2, 20.1]}}
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    om = OpenMeteoHttpClient(client=client)
    s = om.forecast_summary(42.36, -71.06)
    assert s == {"summary": "Hourly temperature", "temp_c": 19.2, "precip_prob": 0.0}


def test_open_meteo_retry_then_success():
    payload = {"current_weather": {"temperature": 25.0}}
    ft = FakeTransport([
        (503, {}, b""),
        (200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep, retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02))
    om = OpenMeteoHttpClient(client=client)
    s = om.forecast_summary(40.0, -74.0)
    assert s == {"summary": "Current weather", "temp_c": 25.0, "precip_prob": 0.0}
