# Live Task Tree

Purpose: A single source of truth for active work, switches, and status. Update this when starting, switching, or completing tasks. Keep entries short and action-oriented.

Legend: [ ] not-started · [~] in-progress · [x] completed · [↺] switched/paused (notes)

## Today (2025-08-15)

- [x] Audit workspace structure
- [x] Ensure env templates include EXCHANGERATE_API_KEY
  - Notes: exchangerate.host now requires an access key; add EXCHANGERATE_API_KEY to .env/.env.example and settings.
- [x] Wire key into settings (if code)
- [x] Wire VS Code tasks.json (deduplicate test tasks)
- [x] Install deps and run tests
- [x] Add persistent task tracking docs (this file)
- [x] Log iteration in journal

- [~] Build HTTP client shim (timeouts, retries, UA)
  - Notes: create src/utils/http_client.py with injectable transport/sleeper; add tests under test/test_http_client.py
  - Status: Completed

- [~] Migrate exchangerate adapter to HttpClient
  - Notes: create src/tools/exchangerate_api.py; tests in test/test_exchangerate_api.py
  - Status: Completed

- [x] Nominatim HTTP adapter using HttpClient
  - Notes: create src/tools/geocode_nominatim_http.py; tests in test/test_geocode_nominatim_http.py
  - Status: Completed

- [x] Open-Meteo adapter + tests
  - Notes: create src/tools/weather_open_meteo_http.py; tests in test/test_weather_open_meteo_http.py
  - Status: Completed

- [x] WorldTimeAPI adapter + tests
  - Notes: create src/tools/timezone_worldtimeapi_http.py; tests in test/test_timezone_worldtimeapi_http.py
  - Status: Completed

- [x] OSRM adapter + tests
  - Notes: create src/tools/routing_osrm_http.py; tests in test/test_routing_osrm_http.py
  - Status: Completed

- [x] OpenTripMap adapter + tests
  - Notes: create src/tools/opentripmap_http.py; tests in test/test_opentripmap_http.py
  - Status: Completed

- [x] Activities agent + tests
  - Notes: create src/agents/activities.py; propose simple POI selection using OpenTripMap client.
  - Status: Completed

- [x] Validator agent and basic replan loop
  - Notes: create src/agents/validator.py; integrated into orchestrator with radius expansion replan.
  - Status: Completed

- [x] Scheduler agent for day segmentation
  - Notes: create src/agents/scheduler.py; builds DayPlans with morning/afternoon segments.
  - Status: Completed

- [x] CLI instruction parsing + agent registry
  - Notes: Enhanced src/cli/parser.py for natural instructions; added src/agents/registry.py for tier listing.
  - Status: Completed

- [x] LLM abstraction with noop default
  - Notes: create src/utils/llm_client.py; NoopLLMClient for annotation without external calls.
  - Status: Completed

## Today (2025-08-16) - Current Work

- [x] Update task tree per rules
- [x] Update project journal per rules  
- [x] Update live overview per rules
- [x] Implement pacing-aware segmentation (easy/normal/packed)
  - Notes: Enhanced parser to detect pace keywords; scheduler now varies segments per day based on preferences.

- [x] Implement interests input via CLI (--interests flag)
  - Notes: Add CLI flag to accept interests list; wire into ActivitiesAgent for POI kind filtering.
  - Status: Completed

- [x] Real LLM client gated behind OPENAI_API_KEY
  - Notes: Added OpenAILLMClient with fallback to NoopLLMClient when API key unavailable.
  - Status: Completed

## Backlog
- [ ] Multi-leg scheduling support
- [ ] Output to file (--out itinerary.json)
- [ ] Budget and calendar agents

## Switching Policy

- When switching mid-stream: mark the current task with [↺], add a one-line reason and link the follow-up task. Start the new task by marking it [~]. On return, flip [↺] back to [~]. Document the switch in the Project Journal.
