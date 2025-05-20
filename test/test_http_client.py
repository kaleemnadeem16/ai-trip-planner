from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from src.utils.http_client import HttpClient, HTTPError, RetryPolicy


# Fake transport to control responses in tests
class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method: str, url: str, headers: Dict[str, str], body: Optional[bytes], timeout: int) -> Tuple[int, Dict[str, str], bytes]:
        self.calls.append((method, url, headers, body, timeout))
        if not self.responses:
            return 200, {}, b"{}"
        status, hdrs, body_bytes = self.responses.pop(0)
        return status, hdrs, body_bytes


def no_sleep(_):
    pass


def test_http_client_success_json():
    ft = FakeTransport([(200, {"Content-Type": "application/json"}, json.dumps({"ok": True}).encode("utf-8"))])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    data = client.get_json("https://example.com/api")
    assert data == {"ok": True}
    assert len(ft.calls) == 1


def test_http_client_retry_then_success():
    ft = FakeTransport([
        (503, {}, b"temporary"),
        (200, {"Content-Type": "application/json"}, b"{\"ok\":true}")
    ])
    client = HttpClient(retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02), transport=ft, sleeper=no_sleep)
    data = client.get_json("https://example.com/api")
    assert data == {"ok": True}
    assert len(ft.calls) == 2


def test_http_client_retry_then_fail():
    ft = FakeTransport([
        (503, {}, b"temporary-1"),
        (503, {}, b"temporary-2"),
        (503, {}, b"temporary-3")
    ])
    client = HttpClient(retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02), transport=ft, sleeper=no_sleep)
    try:
        client.get_json("https://example.com/api")
        assert False, "Expected HTTPError"
    except HTTPError as e:
        assert e.status == 503
