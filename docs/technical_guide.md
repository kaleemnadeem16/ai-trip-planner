# Technical Guide — Multi-Agent Trip Planner (Docs-First)

This guide specifies the technical contracts, data schemas, orchestration logic, and free/public tool integrations for the new multi-agent system. No code is implemented yet; these are the source-of-truth interfaces for the build.

## Core Contracts (Agent Interfaces)

All agents implement a minimal interface:
- name: string
- inputs: JSON matching schema from Orchestrator
- outputs: JSON adhering to declared pydantic models
- side-effects: none (agents write to Blackboard via Orchestrator only)

Execution contract:
- execute(request: AgentRequest, ctx: OrchestratorContext) -> AgentResponse
- must validate input schema on entry and output schema on exit

Error modes:
- ValidationError (input/output schema mismatch)
- ToolError (tool adapter failure)
- ConstraintConflict (cannot satisfy constraints)
- RateLimit/Timeout (tool throttling)

Success criteria:
- Produces schema-valid output
- Adds/updates the correct Blackboard keys
- Emits advisory messages when degrading gracefully

## Data Schemas (abbrev.)

TripRequest
- origin: string | {detect: true}
- legs: [LegRequest]
- global_budget?: Money
- preferences?: {pace: easy|normal|packed, interests: [string], mobility?: string}
- constraints?: {must_visit_global: [POI], date_range?: [start,end]}

LegRequest
- from: Place
- to: Place
- dates: {fixed?: [start,end], duration_days?: int}
- must_visit?: [POI]
- budget?: Money

Place {query: string, lat?: number, lon?: number}
POI {name: string, category?: string, lat?: number, lon?: number, open_hours?: string}
Money {amount: number, currency: string}

Itinerary
- days: [DayPlan]
- totals: {budget_by_category: map, distance_km: number}
- artifacts?: {ics_path?: string, json_path?: string}

DayPlan {date: string, segments: [ScheduledItem], notes?: string, weather?: Weather}
ScheduledItem {kind: 'flight'|'hotel'|'activity'|'transit'|'meal'|'buffer', title: string, start: string, end: string, tz: string, location?: Place, cost?: Money, details?: any}
Weather {summary: string, temp_c: number, precip_prob: number}

All schemas will be defined in `orchestrator/schemas.py` (future).

## Orchestrator Logic

1) Parse/Decompose: Task Decomposer turns NL into TripRequest, resolving per-leg details, must-visits, and budgets.
2) Context Fetch: Geocode places; determine timezones; pull weather and currency rates; store in Blackboard.
3) Plan Compose:
    - Activities Agent: choose POIs per leg (include must-visits first) with opening hours.
    - Routing Agent: estimate travel times; detect tight schedules.
    - Hotel Agent: options near activity clusters and transit; within budget per leg.
    - Flight Agent: propose time windows and search links (due to limited free APIs).
4) Budget Allocation: Budget Agent assigns per-leg/day allocations; flags overruns.
5) Scheduling: Calendar Agent arranges segments, buffers, and meals; Weather Agent proposes swaps.
6) Validation: QA Agent runs checks; Orchestrator loops back to adjust a bounded number of times.
7) Output: Composer writes JSON and optional ICS, and returns human-readable summary.

Parallelization policy:
- Context fetch and POI discovery per leg can run in parallel.
- Routing depends on POIs; scheduling depends on hotel/POI/flight windows.

## Tool Adapters (Free/Public)

All tools are thin adapters with: name, inputs, outputs, error handling, backoff, caching.

Geocoding (OpenStreetMap Nominatim)
- Input: text query
- Output: lat/lon, display_name, type
- Rate/courtesy: set User-Agent, cache, throttle

POIs (OpenTripMap)
- Input: lat/lon + radius or city name
- Output: list of POIs with categories, possible hours/links

Weather (Open-Meteo)
- Input: lat/lon + date(s)
- Output: daily/hourly temps, precipitation, conditions

Timezone (worldtimeapi.org)
- Input: lat/lon or area name
- Output: tz name, offset

Currency (exchangerate.host or Frankfurter)
- Input: from/to currency
- Output: rate

Routing (OSRM or OpenRouteService)
- Input: coordinates list, profile (walk/drive)
- Output: distance, duration, route polyline (optional)

Events (Ticketmaster, optional)
- Input: city + date range
- Output: events list

IP Location (ipapi/ipinfo, optional)
- Input: none
- Output: approximate location; user must opt in

Fallbacks:
- When a tool is unavailable: provide advisory text and a prefilled web search link.

## Validation Rules (selected)

- No overlapping segments per day; enforce min 15–30 min transfer buffers.
- Opening hours honored; if closed, move or swap.
- Travel time + activity duration must fit within day bounds.
- Budgets cannot go negative; if exceeded, propose trade-offs.
- Timezones consistent across segments; convert all to local time for display.

## Testing Strategy

- Unit: each agent with fixture-based tool responses; schema validation tests.
- Integration: multi-leg trip through Orchestrator with mocked tools; verify re-planning.
- Contract: tool adapters’ I/O against recorded cassettes (VCR-like) or local fixtures.
- Snapshot: serialize final Itinerary JSON and compare stable fields.
- Rate-limit etiquette: simulate 429s and verify backoff and caching.

## Configuration (env-first)

Environment variables (no secrets in repo):
- OTM_API_KEY (OpenTripMap, optional)
- TICKETMASTER_API_KEY (optional)
- TOOL_TIMEOUT_MS, TOOL_RETRIES
- ENABLE_IP_LOCATION=false|true

Runtime toggles:
- USE_PUBLIC_OSRM=true|false
- ENABLE_EVENTS=false|true
- MAX_REPLAN_CYCLES (default: 3)

### Setup & Environment

1) Create a `.env` at repo root (see `.env.example`) and populate keys if needed. See `docs/api_keys_guide.md` for how to obtain optional keys.
2) Recommended default values:

```
ENABLE_IP_LOCATION=false
USE_PUBLIC_OSRM=true
ENABLE_EVENTS=false
TOOL_TIMEOUT_MS=8000
TOOL_RETRIES=2
OTM_API_KEY=
TICKETMASTER_API_KEY=
IPINFO_TOKEN=
IPAPI_KEY=
```

3) Keep `.env` out of version control; add it to `.gitignore`.

## Output Artifacts

- Human-readable itinerary (Markdown/plain text)
- JSON plan (strict schema)
- ICS calendar (per-day events)
- CSV budget breakdown

## Build Notes (later implementation)

- Prefer Python 3.10+; Pydantic for schemas; Requests/HTTPX for tools; simple LLM optional for natural language decomposition, but we can start with rule-based parser to keep it free.
- No paid APIs required; all tools configurable and optional.

This guide is the authoritative reference for implementing the agents, tools, orchestration, and validation in the next phase.

## Verified Endpoints — Quick Reference

- Geocoding — Nominatim
    - Search: https://nominatim.openstreetmap.org/search?format=jsonv2&q={query}
    - Notes: Respect usage policy (max ~1 req/sec/IP), set a descriptive User-Agent and optional Referer/email; cache results.

- Weather — Open-Meteo
    - Forecast: https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m
    - Notes: No API key required.

- Timezone — WorldTimeAPI
    - List: https://worldtimeapi.org/api/timezone
    - Specific TZ: https://worldtimeapi.org/api/timezone/{Area}/{Location}
    - Client IP: https://worldtimeapi.org/api/ip
    - Notes: No key required.

- Currency — exchangerate.host (APILayer)
    - Base: https://api.exchangerate.host/
    - Convert: /convert?from=USD&to=EUR&amount=100&access_key=YOUR_KEY
    - Other: /live, /historical, /timeframe, /change (plan dependent)
    - Notes: API key now required per current docs; free tier available.

- Routing — OSRM public server
    - Base: https://router.project-osrm.org
    - Route: /route/v1/{profile}/{lon,lat;lon,lat}[?overview=false]
    - Table/Matrix: /table/v1/{profile}/{coords}
    - Other: /nearest, /match, /trip, /tile
    - Notes: No key; courtesy usage only.

- POIs — OpenTripMap
    - Base: https://api.opentripmap.com/0.1/en/places
    - Radius: /radius?radius={m}&lon={lon}&lat={lat}&apikey=YOUR_KEY
    - Notes: API key required; docs site may be intermittently unavailable, but API base is stable.

- Events — Ticketmaster Discovery API (optional)
    - Root: https://app.ticketmaster.com/discovery/v2/
    - Events: /events.json?countryCode=US&apikey=YOUR_KEY
    - Notes: Key required; rate limits ~5 rps, 5000/day.

- IP Geolocation (optional)
    - ipinfo: https://api.ipinfo.io/lite/me?token=YOUR_TOKEN (or https://ipinfo.io/json?token=...)
    - ipapi: https://ipapi.co/json/ (client IP) or https://ipapi.co/{ip}/json/
    - Notes: Tokens optional for light usage; add when available.
