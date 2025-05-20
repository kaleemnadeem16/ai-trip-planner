# Project Overview (Live, Curated)

Purpose: The current, accurate snapshot of the system—architecture, modules, and capabilities.

Current Architecture Snapshot
- Central Orchestrator with Blackboard memory.
- Multi-tier agents:
  - planning: TaskDecomposer (normalize/defaults), BudgetAgent (planned), CalendarAgent (planned)
  - enrichment: ActivitiesAgent (POIs via OpenTripMap)
  - validation: ValidatorAgent (issues + simple replan)
  - scheduling: SchedulerAgent (DayPlans with morning/afternoon segments)
- Real HTTP-backed tools using a shared HttpClient: Nominatim (geocode), Open-Meteo (weather), WorldTimeAPI (timezone), exchangerate.host (currency), OSRM (routing), OpenTripMap (POIs).
- CLI instruction parsing: accepts natural "from X to Y" or "plan a trip to Y from X" with optional dates.
- Pydantic v2 models for TripRequest/Itinerary; model serialization via `model_dump()`; config via .env.
- LLM abstraction: NoopLLMClient (default, free) for day notes; real LLM optional via OPENAI_API_KEY.

Agents & Responsibilities (current)
- TaskDecomposer: normalize TripRequest; set default durations; placeholder origin detect marker.
- ActivitiesAgent: suggests POIs using OpenTripMap and context geocodes.
- ValidatorAgent: checks for missing geocodes and insufficient activities; triggers simple replan (radius bump).

Tools & Integrations (current)
- Geocode: OSM Nominatim (no key) — HTTP adapter using shared client.
- Weather: Open-Meteo (no key) — HTTP adapter using shared client.
- Timezone: worldtimeapi.org (no key) — HTTP adapter using shared client.
- Currency: exchangerate.host (key required) — HTTP adapter using shared client; env: EXCHANGERATE_API_KEY.
- Routing: OSRM public server (no key) — HTTP adapter using shared client.
- OpenTripMap: POIs (key required) — HTTP adapter using shared client; env: OTM_API_KEY, OTM_DEFAULT_RADIUS.

Schemas (current)
- TripRequest: origin, legs, budgets, preferences, constraints.
- LegRequest: from, to, dates (fixed [start,end] or duration_days).
- Itinerary: days[], totals, artifacts (includes `activities` and a minimal `schedule` artifact when activities exist).

Folder Structure (key paths)
- src/config/settings.py — .env-backed settings.
- src/orchestrator/{blackboard.py, orchestrator.py, schemas.py}
- src/agents/{decomposer.py, activities.py, validator.py}
- src/tools/{geocode_nominatim.py, weather_open_meteo.py, timezone_worldtimeapi.py, currency_exchangerate.py, routing_osrm.py}
- src/tools/exchangerate_api.py — HTTP exchangerate.host adapter
- src/tools/geocode_nominatim_http.py — HTTP Nominatim adapter
- src/tools/weather_open_meteo_http.py — HTTP Open-Meteo adapter
- src/tools/timezone_worldtimeapi_http.py — HTTP WorldTimeAPI adapter
- src/tools/routing_osrm_http.py — HTTP OSRM adapter
- src/tools/opentripmap_http.py — HTTP OpenTripMap adapter (radius)
- src/utils/http_client.py — Shared HTTP client with retries/backoff and User-Agent
- test/ — 35 tests passing.
- main.py — CLI entry; prints plan JSON.

Environment configuration (current)
- Base URLs and UA/key env vars for tools: NOMINATIM_BASE_URL, NOMINATIM_USER_AGENT, OPEN_METEO_BASE_URL, WORLDTIMEAPI_BASE_URL, EXCHANGERATE_BASE_URL, OSRM_BASE_URL, OTM_BASE_URL, TICKETMASTER_BASE_URL, IPINFO_BASE_URL, IPAPI_BASE_URL, OTM_DEFAULT_RADIUS, OTM_API_KEY, EXCHANGERATE_API_KEY.

Open TODOs (brief)
- Pacing-aware day segmentation (easy/normal/packed) to vary segments per day
- Interests input via CLI to steer POI selection and scheduling
- Real LLM client integration (gated by OPENAI_API_KEY)
- Multi-leg scheduling and budget/calendar agents

Out of Scope (for now)
- Paid APIs; live booking; authentication flows.
