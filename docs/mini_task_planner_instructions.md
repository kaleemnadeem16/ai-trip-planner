
# Agentic Trip Planner — Usage & Instructions (Updated)

This document explains how to ask for plans, how the system interprets complex constraints, and what to expect in the outputs. No code changes here—this is the operating guide for the new multi-agent orchestrator.

## What You Can Ask

Simple:
- “Plan a 4-day trip to New York with a $1200 budget.”

Intermediate:
- “Plan a trip from my location to New York for 5 days under $1500. Must visit MoMA and Central Park.”

Complex (multi-city, per-leg constraints):
- “Plan: Lahore → New York (Sep 10-12, must: MoMA), New York → Boston (Sep 13-16, must: MIT Museum, budget $500), Boston → Montreal (5 days, budget $900). Total budget $3000.”

## Input Patterns

The system recognizes these fields (explicit or implied):
- Origin: a city/country or “my location” (will request consent to detect via IP).
- Destinations: one or many (A→B→C→…).
- Dates: fixed ranges per leg or overall duration.
- Budgets: global total and/or per-leg amounts (with currency).
- Must-visit: POIs for each destination.
- Preferences: pace (easy/normal/packed), interests (art, food, outdoors), mobility constraints, accommodation class.

You can combine them freely in natural language; the Task Decomposer will extract a structured TripRequest.

## How The System Works (at a glance)

1) Orchestrator parses your request into a trip graph (legs, dates, constraints).
2) Tools fetch geocodes, time zones, weather forecasts, currency rates.
3) Agents propose POIs/activities, routing times, hotels near clusters, and flight time windows with search links.
4) Budget Agent allocates money per leg/day and flags overruns.
5) Calendar Agent assembles a day-by-day plan with buffers; Weather Agent suggests swaps.
6) Validator checks feasibility; the Orchestrator re-plans a few times if conflicts are found.
7) You receive a readable itinerary plus JSON (and optionally ICS calendar).

## Examples You Can Try (phrasing)

- “3 days in NYC next month, $800 total, must: Central Park, Broadway show.”
- “From Karachi to Istanbul 7 days in October, museums focus, $1800, mid-range hotels.”
- “A→B→C: Rome (2d) → Florence (2d) → Venice (3d), art and food, €2000, prefer trains.”

## Clarifications & Assumptions

- If dates aren’t provided, the system uses durations and typical opening hours for feasibility.
- If origin is “my location”, IP-based detection will only run with your consent and can be disabled.
- Prices for flights/hotels may be estimates with booking search links due to limited free APIs.
- If per-leg budgets conflict with your must-visit list, you’ll get trade-off suggestions (e.g., fewer paid activities or lower hotel class).

## Outputs

- Itinerary (human-readable): by day, with times, POIs, transit, meals, and tips.
- JSON plan: machine-readable schema for debugging or further processing.
- Optional: ICS calendar file and CSV budget breakdown.
- Links: booking/search links for flights/hotels when live pricing isn’t available.

## Known Limitations

- Free APIs have rate limits; large multi-city plans may throttle. We cache and back off politely.
- Some POI opening hours are incomplete in open datasets; the Validator will flag uncertainties.
- Routing ETAs are estimates; add buffers for real-world variability.

## Privacy

- No PII stored by default. Origin detection is opt-in and can be disabled.
- API keys live in your local environment only; never shared or committed.

## Quick Setup (before coding phase)

- Create a `.env` at the project root using `.env.example` as a template.
- If you want richer POIs/events or IP origin detection, obtain keys following `docs/api_keys_guide.md`.
- Keep `.env` private; it will be ignored by Git.

## Troubleshooting (once implemented)

- Missing dates → add fixed dates or durations per leg.
- Over budget → increase total, relax must-visits, or accept lower accommodation class.
- Tool errors (rare) → retry later; the system will degrade with search links.
