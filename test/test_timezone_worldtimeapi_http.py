from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from src.tools.timezone_worldtimeapi_http import WorldTimeApiHttpClient
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


def test_worldtimeapi_timezone_for_ip_success():
    payload = {"timezone": "America/New_York"}
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    w = WorldTimeApiHttpClient(client=client)
    tz = w.timezone_for_ip()
    assert tz == "America/New_York"


def test_worldtimeapi_retry_then_success():
    payload = {"timezone": "Europe/Paris"}
    ft = FakeTransport([
        (503, {}, b""),
        (200, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep, retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02))
    w = WorldTimeApiHttpClient(client=client)
    tz = w.timezone_for_ip("1.2.3.4")
    assert tz == "Europe/Paris"


def test_worldtimeapi_malformed_returns_none():
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps({"foo": "bar"}).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    w = WorldTimeApiHttpClient(client=client)
    tz = w.timezone_for_ip("8.8.8.8")
    assert tz is None
