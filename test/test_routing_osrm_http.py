from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from src.tools.routing_osrm_http import OSRMHttpClient
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


def test_osrm_route_distance_success():
    payload = {"routes": [{"distance": 306000.0}]}
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    osrm = OSRMHttpClient(client=client)
    km = osrm.route_distance_km((42.36, -71.06), (40.71, -74.0))
    assert km == 306.0


def test_osrm_retry_then_success():
    payload = {"routes": [{"distance": 10000.0}]}
    ft = FakeTransport([
        (503, {}, b""),
        (200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep, retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02))
    osrm = OSRMHttpClient(client=client)
    km = osrm.route_distance_km((0.0, 0.0), (0.1, 0.1))
    assert km == 10.0


def test_osrm_malformed_returns_none():
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps({"foo": "bar"}).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    osrm = OSRMHttpClient(client=client)
    km = osrm.route_distance_km((10.0, 10.0), (11.0, 11.0))
    assert km is None
