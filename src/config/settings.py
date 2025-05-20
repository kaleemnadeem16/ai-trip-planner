from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _getenv(key: str, default: str = "") -> str:
    value = os.getenv(key)
    return value if value is not None else default


@dataclass
class LLMSettings:
    provider: str = "openai"
    api_key: str | None = _getenv("OPENAI_API_KEY")
    model: str = _getenv("OPENAI_MODEL", "gpt-4.1-nano")
    temperature: float = float(_getenv("LLM_TEMPERATURE", "0.3"))
    max_tokens: int = int(_getenv("LLM_MAX_TOKENS", "1200"))
    top_p: float = float(_getenv("LLM_TOP_P", "1.0"))
    presence_penalty: float = float(_getenv("LLM_PRESENCE_PENALTY", "0.0"))
    frequency_penalty: float = float(_getenv("LLM_FREQUENCY_PENALTY", "0.0"))
    retries: int = int(_getenv("LLM_RETRIES", "2"))
    timeout_ms: int = int(_getenv("LLM_TIMEOUT_MS", "20000"))


@dataclass
class ToolSettings:
    enable_ip_location: bool = _getenv("ENABLE_IP_LOCATION", "false").lower() == "true"
    use_public_osrm: bool = _getenv("USE_PUBLIC_OSRM", "true").lower() == "true"
    enable_events: bool = _getenv("ENABLE_EVENTS", "false").lower() == "true"
    timeout_ms: int = int(_getenv("TOOL_TIMEOUT_MS", "8000"))
    retries: int = int(_getenv("TOOL_RETRIES", "2"))
    # Optional keys
    otm_api_key: str | None = _getenv("OTM_API_KEY")
    ticketmaster_api_key: str | None = _getenv("TICKETMASTER_API_KEY")
    ipinfo_token: str | None = _getenv("IPINFO_TOKEN")
    ipapi_key: str | None = _getenv("IPAPI_KEY")
    exchangerate_api_key: str | None = _getenv("EXCHANGERATE_API_KEY")
    # Base URLs and client headers (override as needed)
    nominatim_base_url: str = _getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org/search") or "https://nominatim.openstreetmap.org/search"
    nominatim_user_agent: str = _getenv("NOMINATIM_USER_AGENT", "mini-task-planner/0.1") or "mini-task-planner/0.1"
    open_meteo_base_url: str = _getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast") or "https://api.open-meteo.com/v1/forecast"
    worldtimeapi_base_url: str = _getenv("WORLDTIMEAPI_BASE_URL", "https://worldtimeapi.org/api") or "https://worldtimeapi.org/api"
    exchangerate_base_url: str = _getenv("EXCHANGERATE_BASE_URL", "https://api.exchangerate.host") or "https://api.exchangerate.host"
    osrm_base_url: str = _getenv("OSRM_BASE_URL", "https://router.project-osrm.org") or "https://router.project-osrm.org"
    otm_base_url: str = _getenv("OTM_BASE_URL", "https://api.opentripmap.com/0.1/en/places") or "https://api.opentripmap.com/0.1/en/places"
    ticketmaster_base_url: str = _getenv("TICKETMASTER_BASE_URL", "https://app.ticketmaster.com/discovery/v2") or "https://app.ticketmaster.com/discovery/v2"
    ipinfo_base_url: str = _getenv("IPINFO_BASE_URL", "https://ipinfo.io") or "https://ipinfo.io"
    ipapi_base_url: str = _getenv("IPAPI_BASE_URL", "https://ipapi.co") or "https://ipapi.co"
    # Defaults for tool behaviors
    otm_default_radius: int = int(_getenv("OTM_DEFAULT_RADIUS", "3000"))


@dataclass
class AppSettings:
    max_replan_cycles: int = int(_getenv("MAX_REPLAN_CYCLES", "3"))


@dataclass
class Settings:
    llm: LLMSettings = field(default_factory=LLMSettings)
    tools: ToolSettings = field(default_factory=ToolSettings)
    app: AppSettings = field(default_factory=AppSettings)


def get_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings()
