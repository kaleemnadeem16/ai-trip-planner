# Agentic Trip Planner — Project Overview (Updated)

## Purpose

Design a multi-agent, tool-augmented trip planner that can handle both simple and highly complex requests: multi-city itineraries with per-leg dates and budgets, must-visit places, origin inference, and constraint-aware scheduling with live data (weather, time zones, routing, currency).

## What’s New vs Previous Version

- Central Orchestrator coordinating multiple specialized agents (flight, hotel, POI/activities, routing, weather, budget, calendar, validator).
- Free/public API tooling via adapters (Open-Meteo, OpenStreetMap/Nominatim, OSRM, exchangerate.host, worldtimeapi.org, OpenTripMap, optional Ticketmaster).
- Trip represented as a structured graph of legs/days/segments; strict schema validation and re-planning loops for conflicts.
- Graceful degradation when paid data isn’t available (search links and heuristics instead of quoting prices where APIs are limited).

## Capabilities

- Plan trips from “my location” (with explicit consent) or specified origins.
- Single city or multi-city A→B→C→… with per-leg constraints.
- Must-visit lists per destination; per-destination budgets and optional date windows.
- Weather-aware, time-aware, routing-aware schedules with buffers.
- Output: human-readable itinerary plus machine artifacts (JSON plan, optional ICS calendar, CSV budget).

## Example Scenarios

- “Plan a trip to New York for 5 days with a $1500 budget. Must visit MoMA and Central Park.”
- “Plan from Lahore to NYC (Sep 10-12), to Boston (Sep 13-16, must: MIT Museum), to Montreal (5 more days), total budget $3000.”
- “Plan a weekend in Paris next month with focus on art museums and bakeries. Budget €800.”

## Non-Goals

- Live booking or guaranteed prices. We provide options, estimates, and search links.
- Paid/closed APIs. Prefer free options; paid integrations can be optional toggles later.

## Architecture Snapshot

- Orchestrator + Agents + Tool Adapters + Blackboard Memory + Output Composer.
- Parallelize context gathering; serialize dependent steps (e.g., routing after POIs).
- Deterministic validations with bounded re-plan cycles.

## Deliverables (Docs-First)

- Architecture explanation (this repo) detailing agents and tools.
- Technical guide for interfaces, schemas, and tool usage.
- Rebuild plan/roadmap with milestones.
- Development rules tailored to agents/tools and public API usage etiquette.
- Instructions with example prompts and expected outputs.

## Risks & Mitigations

- Free API limits/rate caps → caching, jitter, user-adjustable tool toggles.
- Missing flight/hotel free data → generate search links and heuristic options.
- Complex constraints → explicit validator and constraint manager agents.

## Success Criteria

- Handles complex multi-leg inputs without manual intervention.
- Produces coherent, feasible schedules respecting opening hours/transit/weather.
- Budgets allocated per leg/day with clear breakdown and trade-offs.
- Outputs are reproducible (JSON) and user-friendly (readable + ICS optional).
