## 2025-08-15
- Added pytest to requirements and fixed dataclass defaults + Pydantic validator migration.
- Created minimal CLI (main.py) to run without errors.
- Implemented TaskDecomposer (rule-based) and placeholder tool adapters: NominatimClient, OpenMeteoClient.
- Wired Orchestrator to decomposer and basic context enrichment (fake geocode + weather).
- Added tests for decomposer and tools; total tests now 7 passing.

## 2025-08-15 (later)
- Extended ToolSettings to include base URLs and user-agent env vars for all free APIs.
- Augmented .env and .env.example with API base URLs and OTM_DEFAULT_RADIUS.
- Added adapters: WorldTimeApiClient (timezone), ExchangeRateClient (currency), OSRMClient (routing).
- Added tests for the new adapters; resolved floating-point rounding in currency conversion.
- All tests passing (10).

## 2025-08-15 (task tracking & env updates)
- Added a persistent `rules/task_tree.md` to track active tasks, switches, and backlog.
- Updated `.env.example` and `.env` to include `EXCHANGERATE_API_KEY` due to exchangerate.host key requirement.
- Wired `EXCHANGERATE_API_KEY` into `ToolSettings` in `src/config/settings.py` (no behavior change yet—adapter remains placeholder).
- Deduplicated VS Code tasks and added a "Run app" task; removed invalid problemMatcher.
- Documented a Switching Policy in `task_tree.md` to mark paused tasks with [↺] and log switches here.

## 2025-08-15 (HTTP client + exchangerate adapter)
- Added `src/utils/http_client.py` with retry/backoff and UA; tests added under `test/test_http_client.py`.
- Implemented `src/tools/exchangerate_api.py` using the shared HttpClient.
- Added tests `test/test_exchangerate_api.py` covering success, retry, and unexpected response.
- All tests passing (13). Next: migrate more adapters to HttpClient.

## 2025-08-15 (Nominatim HTTP adapter)
- Added `src/tools/geocode_nominatim_http.py` using the shared HttpClient.
- Added tests `test/test_geocode_nominatim_http.py` for success, retry, and malformed data.
- Incremental step toward migrating all adapters to common client.

## 2025-08-15 (Open-Meteo & WorldTimeAPI adapters)
- Added `src/tools/weather_open_meteo_http.py` and tests `test/test_weather_open_meteo_http.py`.
- Added `src/tools/timezone_worldtimeapi_http.py` and tests `test/test_timezone_worldtimeapi_http.py`.
- Both use the shared HttpClient with retry/backoff and are covered by success and retry tests.

## 2025-08-15 (OSRM routing HTTP adapter)
- Added `src/tools/routing_osrm_http.py` and tests `test/test_routing_osrm_http.py`.
- Uses the shared HttpClient; returns kilometers from route distance meters.

## 2025-08-15 (OpenTripMap HTTP adapter)
- Added `src/tools/opentripmap_http.py` for radius search with API key.
- Added tests `test/test_opentripmap_http.py` for success, key requirement, and retry behavior.

## 2025-08-15 (Activities agent & orchestration)
- Created `src/agents/activities.py` with a simple POI selection based on interests → kinds mapping.
- Wired ActivitiesAgent into Orchestrator when OTM_API_KEY is set; artifacts.activities now recorded.
- Added tests `test/test_activities_agent.py` for agent behavior and orchestrator enrichment.

## 2025-08-15 (Validator agent & simple replan)
- Created `src/agents/validator.py` to detect missing geocode/insufficient activities.
- Orchestrator now performs a single replan pass that increases OTM radius if activities are insufficient.
- Tests added in `test/test_validator_agent.py` and `test/test_activities_agent.py::test_orchestrator_replans_when_insufficient`.

## 2025-08-15 (pydantic migration + minimal schedule)
- Summary: Replaced deprecated `pydantic` `.dict()` calls with `.model_dump()` in orchestrator; added a lightweight schedule artifact.
- Changes: Edited
- Files/Areas: `src/orchestrator/orchestrator.py` (model_dump usage; add `artifacts.schedule` based on first two activities), `rules/task_tree.md` (mark migration done; note schedule artifact).
- Rationale: Remove Pydantic v2 deprecation warnings and provide a minimal, non-breaking structure toward day segmentation.
- Verification: Test suite green (35 passed); no new warnings.
- Follow-ups: Implement proper day segmentation using `DayPlan`/`ScheduledItem` with pacing rules; migrate any remaining placeholders to shared `HttpClient`.

## 2025-08-16 (CLI instruction parsing + agent registry + LLM abstraction)
- Summary: Enhanced CLI to accept natural instructions; added agent registry for multi-tier tracking; introduced LLM abstraction with noop default.
- Changes: Added/Edited
- Files/Areas: 
  - `src/cli/parser.py` (natural instruction parsing with variants and date optionality)
  - `src/agents/registry.py` (agent tier tracking)
  - `src/utils/llm_client.py` (LLM abstraction with NoopLLMClient)
  - `main.py` (argparse, --instruction, --list-agents flags)
  - `src/orchestrator/orchestrator.py` (LLM annotation for day notes)
  - Tests added for parser variants, agent registry, LLM noop
- Rationale: Enable human-like instruction input without structured JSON; provide visibility into multi-agent architecture; prepare LLM integration point safely.
- Verification: Test suite green (43 passed); CLI accepts "from X to Y" and "plan a trip to Y from X" with optional dates.
- Follow-ups: Add pacing-aware segmentation; interests input via CLI; optional real LLM client gated by OPENAI_API_KEY.

## 2025-08-16 (Pacing segmentation + interests input + real LLM client)
- Summary: Implemented pacing-aware day segmentation, interests CLI input, and real LLM client with API key gating.
- Changes: Added/Edited
- Files/Areas:
  - `src/cli/parser.py` (pace keyword detection: easy/normal/packed)
  - `src/agents/scheduler.py` (dynamic segment count: 1-3 segments per day based on pace)
  - `main.py` (--interests flag for comma-separated interests list)
  - `src/agents/activities.py` (interests filtering via POI kind mapping)
  - `src/utils/openai_client.py` (real OpenAI client with fallback handling)
  - `src/utils/llm_client.py` (factory pattern for LLM selection)
  - Tests added for pace detection, interests filtering, OpenAI client with key gating
- Rationale: Enable preference-driven itinerary generation; support user interests for relevant POI selection; provide optional advanced LLM features.
- Verification: Test suite green (51 passed); CLI supports pacing and interests; LLM integration works with/without API key.
- Follow-ups: Output to file capability; multi-leg scheduling; budget and calendar agents.

## 2025-08-16 (Full agentic transformation - LLM-driven architecture)
- Summary: Completed transformation to fully agentic app powered by LLM agents with no hardcoded fallbacks.
- Changes: Added/Edited
- Files/Areas:
  - `src/agents/instruction_agent.py` (LLM-powered natural language instruction parsing replacing regex)
  - `src/agents/interest_mapping_agent.py` (LLM-powered interest-to-category mapping replacing hardcoded dictionary)
  - `src/utils/llm_client.py` (NoopLLMClient now enforces LLM requirement instead of fallbacks)
  - `src/utils/openai_client.py` (Fixed model name and token limits for proper API communication)
  - `src/config/settings.py` (Added dotenv loading for proper environment variable access)
  - `main.py` (Added --out flag with automatic output/ folder organization)
  - `.env` (Updated OpenAI model to gpt-3.5-turbo)
- Rationale: Showcase true agentic behavior where LLM understands natural language and makes dynamic decisions instead of hardcoded rules.
- Verification: App successfully parses "plan a relaxed trip to Rome from London for 3 days, I love ancient history and great food" → extracts London/Rome, 3 days, "easy" pace, ["ancient history", "great food"] interests.
- Agentic Features Implemented: Natural language understanding, dynamic interest mapping, pace interpretation, output organization.
- Data Status: Real geocoding (London: 51.49°N, Rome: 41.89°N), real weather (27.6°C), LLM-driven parsing and mapping.

## 2025-08-16 (Real API integration + parser fixes)
- Summary: Migrated orchestrator from placeholder clients to real HTTP clients; fixed instruction parsing for duration phrases; ensured all data sources return real API data.
- Changes: Edited
- Files/Areas:
  - `src/orchestrator/orchestrator.py` (migrated from NominatimClient/OpenMeteoClient to HTTP versions with proper settings)
  - `src/cli/parser.py` (fixed regex to handle "for X days" properly without including in location names)
  - `src/tools/weather_open_meteo_http.py` (added precipitation_probability support for Weather schema compliance)
  - Test files updated to patch correct client names and expect new Weather schema fields
- Rationale: Eliminate placeholder/dummy data throughout app; ensure all geocoding, weather, and activity data comes from real APIs; fix parsing bugs that created malformed location queries.
- Verification: Test suite green (51 passed); CLI now returns real coordinates for London/Paris; weather includes real temperature and precipitation probability.
- Data Status: **All data is now REAL** - geocoding via Nominatim, weather via Open-Meteo, activities via OpenTripMap (when API key provided).
# Project Journal (Append-Only)

Purpose: A chronological log of changes (adds/edits/deletes), decisions, and iterations. We never remove entries; deletions are recorded as such.

Entry template:
- Date (YYYY-MM-DD)
- Summary
- Changes: [Added|Edited|Deleted]
- Files/Areas touched
- Rationale
- Follow-ups/Next steps

Guidelines:
- Append an entry after every iteration.
- Link to relevant PRs/commits.
- Keep it honest; include failures and rollbacks.
