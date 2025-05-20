from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.utils.http_client import HttpClient


@dataclass
class WorldTimeApiHttpClient:
    base_url: str = "https://worldtimeapi.org/api"
    user_agent: str = "mini-task-planner/0.1"
    client: HttpClient = field(default_factory=HttpClient)

    def timezone_for_ip(self, ip: Optional[str] = None) -> Optional[str]:
        # /ip uses requestor IP if none provided
        url = f"{self.base_url}/ip" if ip is None else f"{self.base_url}/ip/{ip}"
        self.client.user_agent = self.user_agent or self.client.user_agent
        data = self.client.get_json(url)
        if isinstance(data, dict):
            tz = data.get("timezone") or data.get("time_zone")
            if isinstance(tz, str) and tz:
                return tz
        return None
