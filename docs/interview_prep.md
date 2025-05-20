# Interview Prep — Multi-Agent Trip Planner (Updated)

## One-liner

I designed a multi-agent trip planner with a central Orchestrator coordinating specialized agents (flights, hotels, POIs, routing, weather, budget, calendar) powered by free/public APIs. It handles complex multi-city constraints, budgets per leg, and must-visit lists, producing a feasible itinerary plus JSON/ICS artifacts.

## Why multi-agent and not a single chain?

- Separation of concerns: each agent owns a domain (tools, heuristics, validations).
- Better constraint handling: explicit Validator and re-plan loops for conflicts.
- Tool-first approach: agents rely on structured tools (Open-Meteo, OSRM, OSM) instead of opaque LLM outputs.
- Extensibility: easy to add Events, Dining, or Safety agents later.

## Key design choices

- Orchestrator + Blackboard memory pattern for shared state.
- Free APIs only: Open-Meteo, OpenStreetMap/Nominatim, OSRM, exchangerate.host, worldtimeapi.org, OpenTripMap.
- Flights/Hotels via search links + heuristics due to limited free pricing APIs.
- Strict schemas with pydantic; Validator enforces feasibility (hours, routing, budgets, tz).

## Likely questions

Q: How do you handle per-leg budgets and dates?  
A: The TripRequest schema models legs with optional fixed dates and budgets. Budget Agent allocates and tracks spend by category; Validator catches overruns and triggers re-plan suggestions (cheaper hotel class, fewer paid activities, reorder days).

Q: How do you ensure opening hours and travel times are respected?  
A: Activities Agent attaches opening hours (where available) from OpenTripMap; Routing Agent estimates ETAs via OSRM; Calendar Agent places buffers; Validator checks overlaps and closed windows.

Q: What if a free API throttles or fails?  
A: Tool adapters use timeouts, retries with backoff, caching, and respectful rate limits. If a tool is unavailable, we degrade gracefully with advisories and prefilled search links.

Q: How do you infer origin when the user says “my location”?  
A: IP-based geolocation via opt-in adapters (ipinfo/ipapi). It’s off by default and can be disabled; otherwise we fall back to asking the user.

Q: Why not live booking/prices?  
A: Free APIs for pricing are limited or restrictive; to keep the project free and personal, we provide heuristics and links with prefilled parameters rather than quoting prices.

## Trade-offs

- Accuracy vs. availability: open datasets can be incomplete; we flag uncertainty and add buffers.
- Speed vs. courtesy: we throttle and cache to respect public services.
- Simplicity vs. power: Orchestrator enforces bounded re-planning to avoid infinite loops.

## Testing approach

- Unit tests for each agent/tool with fixtures and schema validation.
- Integration tests for multi-leg trips with mocked tools and forced conflicts.
- Snapshot tests for final JSON; contract tests for adapter I/O.

## Demo script (when implemented)

1) Show a complex prompt: “Lahore → NYC (Sep 10-12, must: MoMA) → Boston (Sep 13-16, must: MIT Museum) → Montreal (5 days), total $3000.”
2) Walk through Blackboard: geocodes, weather, routing, POIs, budgets.
3) Show Validator catching an hours conflict and re-plan.
4) Present final itinerary.md + plan.json + optional calendar.ics.

## Follow-ups and extensions

- Add Events Agent; Dining Agent with cuisine preferences; Safety/Advisory Agent.
- Persist user preferences; feedback loop to personalize pacing and interests.
- Optional web UI for interactive edits and drag-and-drop schedule adjustments.
