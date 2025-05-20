# Rebuild Plan — Multi-Agent Orchestrated Trip Planner

Start date: Aug 15, 2025  
Goal: Deliver a docs-first, phased roadmap to implement the new central Orchestrator with specialized agents and free API tools.

## Milestones (Phased)

Phase 0 — Docs & Schemas (this work)
- [x] Architecture, Technical Guide, Instructions, Dev Rules
- [ ] Define pydantic schemas (draft): TripRequest, LegRequest, Itinerary, DayPlan, ScheduledItem

Phase 1 — Core Orchestrator & Memory
- [ ] Implement Blackboard store and schema validation utilities
- [ ] Implement Task Decomposer (rule-based first; optional LLM later)
- [ ] Build Orchestrator loop (plan → validate → re-plan up to N cycles)

Phase 2 — Tool Adapters (Free APIs)
- [ ] Geocoding (Nominatim) with caching and polite rate limits
- [ ] Weather (Open-Meteo) per-leg/day
- [ ] Time/Timezone (worldtimeapi.org)
- [ ] Currency (exchangerate.host)
- [ ] Routing (OSRM public server) for walking/driving ETA
- [ ] Optional: Events (Ticketmaster), IP location (opt-in)

Phase 3 — Core Agents
- [ ] Activities Agent (OpenTripMap + heuristics + must-visits)
- [ ] Routing Agent (inter-POI and daily path feasibility)
- [ ] Hotel Agent (clusters and budgets; produce search links)
- [ ] Flight Agent (time windows + search links; no paid APIs)
- [ ] Budget Agent (allocations per leg/day, alerts)

Phase 4 — Scheduling, Validation, and Output
- [ ] Calendar Agent (day-by-day schedule with buffers)
- [ ] Weather Agent (swap activities by forecast)
- [ ] Validator/QA Agent (time overlaps, hours, tz, budgets)
- [ ] Output Composer (Readable itinerary, JSON, ICS, CSV)

Phase 5 — Hardening & UX
- [ ] Caching, retries, backoff, and rate-limit etiquette
- [ ] Config flags for optional tools (events, IP detection)
- [ ] CLI experience and sample prompts
- [ ] Example datasets and fixtures for tests

## Risks & Mitigation

- Free API limits: cache aggressively, throttle, batch calls.
- Incomplete POI hours: include uncertainty markers; suggest alternative days.
- Flight/hotel pricing: stick to search links with parameters; document limitation clearly.
- Multi-city complexity: enforce bounded re-plans and surface trade-offs to user.

## Acceptance Criteria

- Handles inputs from simple (single city) to complex (multi-leg, per-leg budgets/dates, must-visits).
- Produces feasible itineraries honoring opening hours, transit, and budgets.
- Outputs JSON plan and readable text; optionally ICS and CSV.
- All network access via tool adapters with tests and fixtures.

## Example Deliverables

- Example 1: “5 days in NYC, $1500, must: MoMA, Central Park”
- Example 2: “A→B→C two-week plan with per-leg budgets and fixed dates for first leg”
- For each: itinerary.md, plan.json, budget.csv, optional calendar.ics

## Timeline (suggested)

Concrete dates (backdating window):

- May 20–May 24: Phase 0 (docs) and Phase 1 start (schemas, blackboard skeleton)
- May 25–May 29: Phase 1 finish (orchestrator loop) + Phase 2 start (geocoding, weather)
- May 30–June 3: Phase 2 finish (timezone, currency, routing, optional events/IP)
- June 4–June 9: Phase 3 agents (Activities, Routing, Hotel, Flight, Budget)
- June 10–June 14: Phase 4 (Calendar, Weather swaps, Validator, Output Composer)
- June 15–June 18: Phase 5 (hardening, CLI UX, fixtures, docs/demos)

## Go/No-Go Checklist

- Schemas stable; tests for adapters and agents pass
- Orchestrator re-plan loop verified with conflict scenarios
- CLI produces artifacts for at least 3 representative complex prompts

This plan prioritizes free data sources, clarity, and reliability while enabling rich, constraint-aware trip planning.
