from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from src.tools.geocode_nominatim_http import NominatimHttpClient
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


def test_nominatim_http_success():
    payload = [
        {"lat": "42.3601", "lon": "-71.0589", "display_name": "Boston"}
    ]
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    nom = NominatimHttpClient(client=client)
    coords = nom.geocode("Boston, MA")
    assert coords == (42.3601, -71.0589)


def test_nominatim_http_retry_then_success():
    payload = [
        {"lat": "40.7128", "lon": "-74.0060", "display_name": "New York"}
    ]
    ft = FakeTransport([
        (503, {}, b""),
        (200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep, retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02))
    nom = NominatimHttpClient(client=client)
    coords = nom.geocode("New York, NY")
    assert coords == (40.7128, -74.006)


def test_nominatim_http_malformed_returns_none():
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps({"foo": "bar"}).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    nom = NominatimHttpClient(client=client)
    coords = nom.geocode("Somewhere")
    assert coords is None
