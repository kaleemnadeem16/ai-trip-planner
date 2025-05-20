from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

from src.tools.exchangerate_api import ExchangeRateAPI
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


def test_exchangerate_api_convert_result():
    ft = FakeTransport([
        (200, {"Content-Type": "application/json"}, json.dumps({"result": 90.0}).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    api = ExchangeRateAPI(client=client)
    res = api.convert(100, "USD", "EUR")
    assert res == 90.0


def test_exchangerate_api_retry_then_success():
    ft = FakeTransport([
        (503, {}, b""),
        (200, {"Content-Type": "application/json"}, json.dumps({"result": 110.0}).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep, retry_policy=RetryPolicy(retries=2, base_delay=0.01, max_delay=0.02))
    api = ExchangeRateAPI(client=client)
    res = api.convert(100, "EUR", "USD")
    assert res == 110.0


def test_exchangerate_api_unexpected_response_raises():
    ft = FakeTransport([
        (200, {"Content-Type": "application/json"}, json.dumps({"foo": "bar"}).encode("utf-8"))
    ])
    client = HttpClient(transport=ft, sleeper=no_sleep)
    api = ExchangeRateAPI(client=client)
    try:
        api.convert(100, "USD", "GBP")
        assert False, "Expected HTTPError"
    except HTTPError as e:
        assert e.status == 500
