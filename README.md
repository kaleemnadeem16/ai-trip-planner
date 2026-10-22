# AI Trip Planner

A multi-agent trip planner in Python. An LLM-driven central planner decides which specialist agents to call, in what order, over a shared blackboard, and stops after a bounded number of planning cycles.

**Status:** Alpha. The orchestration, language parsing, weather, geocoding and activity lookup are real. Flight, hotel, transport and budget outputs use estimated or mock data, not live prices or bookings.

## How it works

1. The instruction agent turns a natural-language request into a structured trip request (Pydantic schema).
2. The central planning agent looks at the current state and picks the next specialist agent. This repeats until planning is complete or the iteration limit is reached (default 10).
3. Each agent reads from and writes to a shared blackboard. Agents are stateless and reach the outside world only through tools.
4. The itinerary formatter writes the result as plain text.

If an external service is unavailable, agents fall back to estimates and planning continues.

| Agent | Does | Data |
|---|---|---|
| Instruction | Parses the request | OpenAI |
| Central planner | Chooses the next agent | OpenAI |
| Interest mapping | Maps interests to activity categories | Rule-based |
| Activities | Finds places of interest | OpenTripMap (optional key) |
| Weather | Forecast | Open-Meteo |
| Flights, Hotels, Transport | Suggestions and price ranges | Estimated (mock) |
| Budget | Totals the estimates | Estimated (mock) |
| Scheduler, Validator, Formatter | Day-by-day plan, checks, output | Local |

Geocoding uses Nominatim; currency, routing and timezone tools are in `src/tools/`.

## Quick start

Requires Python 3.10+ and an OpenAI API key.

```bash
git clone https://github.com/kaleemnadeem16/ai-trip-planner.git
cd ai-trip-planner
pip install -r requirements.txt
cp .env.example .env     # set OPENAI_API_KEY; OTM_API_KEY (OpenTripMap) is optional

python main.py --interactive
python main.py --instruction "Plan a 5-day trip to Tokyo from London, interested in temples and technology"
```

## Example output

Shortened sample from an earlier run. Flight, hotel and budget figures are mock estimates.

```
Trip Overview: Lahore -> New York (7 days)

Flight Recommendations:
- Emirates EK624: Lahore -> New York (via Dubai), about 14h 45m, ~$1,200 (estimate)

Hotel Recommendations:
- Grand New York Hotel (Downtown): $180/night (estimate)

Weather Forecast: expected conditions and packing recommendations
Daily Schedule: Day 1 arrival and orientation; Day 2 landmarks and museums; ...
Budget Estimates: flights $1,200, hotels $1,260 (7 nights)
```

## Project layout

```
src/
  agents/        specialist agents and the central planning agent
  orchestrator/  blackboard, orchestrator loop, schemas
  tools/         external API wrappers (weather, geocoding, POI, routing, currency, timezone)
  utils/         LLM and HTTP clients
  cli/           argument parsing
  config/        environment settings
test/            pytest tests
main.py
```

## Tests

```bash
python -m pytest test/ -v
```

Covers the config, schemas, CLI parsing, HTTP and tool clients, and several agents. There is no CI workflow yet.

## Limitations

- Flights, hotels, transport and budget are estimates, not live data. Nothing is booked.
- Needs an OpenAI key for planning; no offline mode.
- Free public APIs (Open-Meteo, Nominatim) are used without caching, so heavy use may be rate limited.
- Alpha: interfaces and agent behaviour may change.

## Roadmap

- Replace the mock flight and hotel agents with a real data source.
- Add a CI workflow for the tests.
- Add a web front end.

## License

MIT, see [LICENSE](LICENSE).
