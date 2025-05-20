from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from src.tools.opentripmap_http import OpenTripMapHttpClient
from src.utils.http_client import HttpClient, RetryPolicy, HTTPError


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


def test_otm_radius_success():
    payload = {
        "features": [
            {"properties": {"name": "Museum A", "kinds": "museums"}, "geometry": {"coordinates": [10.0, 20.0]}},
            {"properties": {"name": "Park B", "kinds": "parks"}, "geometry": {"coordinates": [10.1, 20.1]}},
        ]
    }
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    otm = OpenTripMapHttpClient(api_key="key", client=client)
    items = otm.radius_search(20.0, 10.0, radius_m=500, kinds="museums,parks", limit=2)
    assert len(items) == 2
    assert items[0]["name"] == "Museum A"
    assert items[1]["kinds"] == "parks"


def test_otm_requires_key():
    client = HttpClient(transport=lambda *args, **kwargs: (200, {}, b"{}"), sleeper=no_sleep)
    otm = OpenTripMapHttpClient(api_key=None, client=client)
    try:
        otm.radius_search(20.0, 10.0)
        assert False, "Expected HTTPError"
    except HTTPError as e:
        assert e.status == 401


def test_otm_retry_then_success():
    payload = {"features": []}
    ft = FakeTransport([
        (503, {}, b""),
        (200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep, retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02))
    otm = OpenTripMapHttpClient(api_key="key", client=client)
    items = otm.radius_search(0.0, 0.0)
    assert items == []
