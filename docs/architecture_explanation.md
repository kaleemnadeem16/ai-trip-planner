# Project Architecture Explanation - Mini Trip Planner

## System Architecture Overview

The Mini Trip Planner is designed as a modular, sequential AI workflow system that demonstrates advanced orchestration patterns using LangChain. The architecture emphasizes clean separation of concerns, data flow management, and scalable design principles.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │  Input Parser   │    │  Trip Planner   │
│                 │───▶│                 │───▶│   Controller    │
│ Natural Language│    │ Extract Params  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                 LangChain Sequential Chain                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Flight    │───▶│   Hotel     │───▶│     Itinerary       │  │
│  │   Agent     │    │   Agent     │    │      Agent          │  │
│  │             │    │             │    │                     │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Output Format  │    │   Response      │    │  User Display   │
│    Engine       │───▶│   Validator     │───▶│                 │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Design Principles

### 1. Sequential Processing Pattern
**Rationale**: Travel planning has natural dependencies - you need flights before hotels, and both before creating an itinerary.

**Implementation**: LangChain's SequentialChain ensures each agent receives context from previous agents, creating increasingly refined and contextually aware recommendations.

**Benefits**:
- Logical flow mirrors human planning process
- Each step builds upon previous decisions
- Prevents conflicting recommendations
- Enables context-aware decision making

### 2. Agent Specialization
**Concept**: Each agent focuses on a specific domain with specialized knowledge and prompting.

**Flight Agent**:
- Expertise: Airlines, routes, pricing, timing
- Context: Destination, duration, budget
- Output: Flight options with schedules and costs

**Hotel Agent**:
- Expertise: Accommodations, locations, amenities
- Context: Flight details + destination preferences
- Output: Hotels matched to flight schedules and location needs

**Itinerary Agent**:
- Expertise: Local attractions, logistics, timing
- Context: Complete travel and accommodation details
- Output: Detailed daily plans with realistic scheduling

### 3. Data Flow Architecture

```python
# Data transformation through the pipeline
User Input: "Plan a 3-day trip to Istanbul"
     ↓
Parsed Params: {
    "destination": "Istanbul",
    "duration": "3",
    "departure_city": "New York",
    "budget_level": "moderate"
}
     ↓
Flight Agent Output: {
    "flight_recommendations": "Turkish Airlines, $450..."
}
     ↓
Hotel Agent Input: Parsed Params + Flight Output
Hotel Agent Output: {
    "hotel_recommendations": "Hilton Istanbul, near airport..."
}
     ↓
Itinerary Agent Input: All Previous Context
Itinerary Agent Output: {
    "daily_itinerary": "Day 1: Arrive 14:30, check-in..."
# Agentic Trip Planner — Multi-Agent Architecture (New Execution System)

This document defines the new architecture: a multi-level agent system with a central Orchestrator coordinating specialized agents and shared tools. It supports simple to very complex trip requests: multi-city legs (A→B→C→D→E…), per-destination dates and budgets, “must visit” lists, origin inference (from current location), and constraint-aware itinerary building with live data (weather, time zones, currency, POIs).

## Top-Level Overview

Key ideas:
- Central Orchestrator agent that decomposes goals and schedules other agents.
- Specialized agents (flight, hotel, activities/POIs, routing, weather, budget, calendar, etc.).
- Shared tool adapters for free/public APIs (geocoding, weather, time, currency, POIs, routing).
- A common message schema and a shared blackboard-style memory for state and partial results.
- Deterministic constraint handling and re-planning loops when constraints conflict.

High-level flow:
1) User request → 2) Task Decomposition → 3) Constraint & Context Gathering → 4) Plan Synthesis → 5) Validation & Budget Check → 6) User-facing Itinerary

```
User ▶ Orchestrator ▶ Task Decomposer ┐
                                    └▶ Constraint Manager ─┬───────────────┐
                                                                                 │               │
                                                                                 ▼               ▼
                                                             Specialized Agents   Shared Tools
                                                                                 │               │
                                                                                 └──▶ Blackboard Memory ◀──┘
                                                                                                        │
                                                                                                        ▼
                                                                                        Output Composer
```

## Agents and Responsibilities

At minimum (extendable):
- Task Decomposer: Parse NL request into structured trip graph (legs, dates, must-visit, per-leg budget, preferences).
- Constraint Manager: Normalize constraints (time zones, opening hours, travel time, budgets) and detect conflicts.
- Flight Agent: Suggest viable flight options per leg (uses heuristics + live context; see Tools for API notes).
- Hotel Agent: Recommend accommodations per leg, near activities/transit, within budget/date windows.
- Activities Agent (POI): Select must-visits and complementary attractions per leg.
- Routing/Transit Agent: Estimate travel times between POIs/hotel/airports via routing tools.
- Weather Agent: Fetch per-date forecasts, suggest weather-appropriate swaps/alternatives.
- Budget Agent: Allocate and track budget across legs and categories (transport, hotel, food, activities, buffer).
- Calendar Agent: Produce calendar-ready outputs (ICS) and day-by-day schedules.
- Validator/QA Agent: Sanity-check times, feasibility, and format; suggest fixes.

Optional/advanced:
- Events Agent (local events), Safety/Advisory Agent (country advisories), Preference Memory Agent (learns user tastes), Currency Agent (FX conversions), Dining Agent (food recs), Ground Transport Agent (airport transfers, ride estimates).

## Tools (Free/Public APIs only)

We will use only free tiers or open datasets via adapters:
- Geocoding/Places: OpenStreetMap Nominatim (geocode/search), OpenTripMap (POIs, opening hours/categories), Wikidata/Wikipedia (context).
- Weather: Open-Meteo (forecast by lat/lon, no key), NOAA where applicable, Meteostat (historical/climatology).
- Time & Timezone: worldtimeapi.org or TimezoneDB (free tier) to resolve local time/offset.
- Currency: exchangerate.host or Frankfurter.app for FX rates.
- Routing: OSRM public servers (car/walk/bike) or OpenRouteService (free tier) for distances/ETA.
- Location by IP (if needed): ipinfo.io (free tier) or ipapi.co; provide opt-out.
- Events (optional): Ticketmaster Discovery API (free tier) for concerts/events.

Notes on Flights/Hotels: There are few truly free booking/pricing APIs. For personal, non-commercial use we will:
- Prefer heuristic planning (time windows, typical durations, airports) + links to aggregator searches (deeplinks with prefilled params) instead of quoting guaranteed prices.
- Where a free discovery API is available (e.g., Amadeus sandbox for discovery, limited), we’ll integrate via a toggle. Otherwise, we create “search links” to Skyscanner/Google Flights/Booking.com with parameters.

## Data Model (Core Schemas)

TripRequest
- legs: [LegRequest]
- origin: string | {detect: true}
- global_budget: Money? (currency, amount)
- preferences: {pace, interests[], dietary, mobility, accommodation_class}
- hard_constraints: {must_visit[], fixed_dates[], per-leg budgets, time windows}

LegRequest
- from, to (place string or geocode)
- date_range: [start, end] | fixed dates | duration days
- must_visit: [POI]
- budget: Money?

Itinerary
- days: [DayPlan]
- totals: {budget_by_category, distance, buffer_time}
- artifacts: {ics_file, json_plan}

DayPlan
- date
- segments: [ScheduledItem]
- notes, weather, tips

ScheduledItem
- kind: flight | hotel | activity | transit | meal | buffer
- start/end (local time + tz)
- location (lat/lon), title, details, cost_estimate

All inter-agent messages share JSON payloads aligned to the above types. The Validator ensures schema adherence before progressing.

## Orchestration & Execution Model

1) Parse: Task Decomposer converts NL into TripRequest and LegRequests, resolving ambiguities (asks clarifying questions via Orchestrator if essential).
2) Context: Tools fetch geocodes, timezones, weather forecasts, FX rates; Blackboard stores results.
3) Planning: Activities Agent picks POIs respecting must-visit; Routing Agent estimates travel time; Hotel/Flight Agents propose options or search links.
4) Budgeting: Budget Agent allocates budget per leg/day; flags overruns; proposes trade-offs.
5) Scheduling: Calendar Agent arranges a feasible day-by-day schedule with buffers and transit; Weather Agent suggests swaps by forecast.
6) Validation: QA Agent checks conflicts (overlaps, closed hours, impossible routes) and triggers minimal re-plans.
7) Compose Output: Output Composer generates human-readable itinerary + machine artifacts (JSON/ICS/CSV).

Parallelism: Context-gathering and POI discovery can run in parallel per leg. Orchestrator manages dependencies (e.g., routing after POIs, hotels after date windows).

## Memory & State

- Blackboard Memory: central, structured store keyed by trip/leg/day.
- User Profile: persisted preferences (pace, budgets, accessibility) with consent.
- Caching: Geocodes, POIs, routing, weather per (lat, lon, date) cached locally to respect rate limits.

## Constraint Handling & Re-planning

Conflicts the system can resolve:
- Per-leg budget too low → suggest reducing nights, cheaper hotel class, fewer paid activities.
- Must-visit closed on date → shift day or propose alternate.
- Transit time exceeds schedule → reorder or drop low-priority items.
- Weather adverse → indoor alternatives.

The Orchestrator enforces a bounded number of re-plan cycles (e.g., up to 3) and surfaces trade-offs to the user.

## Error Handling & Resilience

- Tool timeouts/retries with exponential backoff.
- Graceful degradation: when a tool is unavailable, return advisory text and a search link.
- Strict input/output validation against schemas; fail-fast with actionable feedback.
- Rate limiting and respectful use of public services; randomized jitter and caching.

## Security & Privacy

- No PII stored by default; explicit opt-in for preference memory.
- API keys via environment variables; never committed.
- IP-based location detection off by default; on with consent and a switch.

## Folder Structure (planning-stage)

Proposed (for future implementation; docs only for now):
```
src/
    orchestrator/
        orchestrator.py            # central agent
        blackboard.py              # shared state/memory
        schemas.py                 # pydantic models for messages
    agents/
        task_decomposer.py
        constraint_manager.py
        flight_agent.py
        hotel_agent.py
        activities_agent.py
        routing_agent.py
        weather_agent.py
        budget_agent.py
        calendar_agent.py
        validator_agent.py
    tools/
        geocoding_opensource.py
        weather_open_meteo.py
        timezone_worldtimeapi.py
        currency_exchangerate_host.py
        routing_osrm.py
        events_ticketmaster.py
    output/
        composer.py                # human-readable + ICS/JSON
```

## Sequence (complex multi-city example)

User: “Plan a 12-day trip from my location: 3 days NYC (must: MoMA, Central Park), 4 days Boston (must: MIT Museum), 5 days Montreal, budget $3000 total; NYC on Sep 10-12; rest flexible.”

1) Task Decomposer → TripRequest with 3 legs, one fixed-date leg, must-visits.
2) Tools → detect origin (if allowed), geocode cities, resolve timezones, pull weather windows, FX rates.
3) Activities Agent → POIs per leg (ensuring must-visits included), opening hours.
4) Routing Agent → inter-POI and city-to-city estimations.
5) Hotel Agent → options near clusters; Budget Agent → allocations per leg.
6) Calendar Agent → daily schedules; Weather Agent → swap outdoor/indoor if needed.
7) Validator → check feasibility; Orchestrator resolves conflicts.
8) Composer → final plan + links for booking searches; export ICS and JSON.

This architecture is purpose-built for the complex cases described, while still handling simple “plan a trip to New York with $X” requests via a subset of agents.
```python
