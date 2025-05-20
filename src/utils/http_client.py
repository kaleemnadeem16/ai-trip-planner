from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple


class HTTPError(Exception):
    def __init__(self, status: int, message: str, body: Optional[str] = None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.body = body


Transport = Callable[[str, str, Dict[str, str], Optional[bytes], int], Tuple[int, Dict[str, str], bytes]]
Sleeper = Callable[[float], None]


@dataclass
class RetryPolicy:
    retries: int = 2
    base_delay: float = 0.5  # seconds
    max_delay: float = 4.0

    def next_delay(self, attempt: int) -> float:
        # exponential backoff with jitter factor
        delay = min(self.max_delay, self.base_delay * (2 ** attempt))
        # simple jitter: scale by 0.8-1.2 range using attempt hash
        jitter = 0.9 + (attempt % 3) * 0.1
        return delay * jitter


@dataclass
class HttpClient:
    user_agent: str = "mini-task-planner/0.1"
    timeout_sec: float = 8.0
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    transport: Optional[Transport] = None
    sleeper: Sleeper = time.sleep

    def _default_transport(self) -> Transport:
        # Lazy import to avoid adding requests as a hard dep; use urllib
        import urllib.request
        import urllib.error

        def _call(method: str, url: str, headers: Dict[str, str], body: Optional[bytes], timeout: int):
            req = urllib.request.Request(url=url, data=body, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = resp.getcode()
                    resp_headers = dict(resp.getheaders())
                    resp_body = resp.read()
                    return status, resp_headers, resp_body
            except urllib.error.HTTPError as e:
                return e.code, dict(e.headers or {}), e.read() if e.fp else b""
            except urllib.error.URLError as e:
                raise HTTPError(0, f"Network error: {e}")

        return _call

    def request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, json_body: Any = None, data: Optional[bytes] = None) -> Tuple[int, Dict[str, str], bytes]:
        method = method.upper()
        headers = {"User-Agent": self.user_agent, **(headers or {})}
        body = data
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")

        transport = self.transport or self._default_transport()

        attempt = 0
        while True:
            status, resp_headers, resp_body = transport(method, url, headers, body, int(self.timeout_sec))
            if status < 400:
                return status, resp_headers, resp_body

            # Retry on 429 and 5xx per policy
            if status in (429, 500, 502, 503, 504) and attempt < self.retry_policy.retries:
                delay = self.retry_policy.next_delay(attempt)
                self.sleeper(delay)
                attempt += 1
                continue

            raise HTTPError(status, f"Request failed for {url}", resp_body.decode("utf-8", errors="ignore"))

    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        status, _headers, body = self.request("GET", url, headers=headers)
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise HTTPError(status, f"Invalid JSON from {url}: {e}")
