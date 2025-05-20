# Development Rules — Agentic Trip Planner (Updated)

These rules guide implementation quality, ethics, and maintainability for the new multi-agent, tool-augmented system.

## Principles

- Docs-first: update docs before code changes to keep the plan authoritative.
- Modular by design: agents and tools are small, testable units.
- Free-first: prefer free/public APIs; paid tools must be optional behind flags.
- Privacy-by-default: no PII storage unless explicit opt-in.
- Graceful degradation: when data isn’t available, provide advisories and links.

## Rules Usage & Documentation Policy

- The `rules/` folder is authoritative for standards and practices.
- Maintain two rule-managed docs:
    1) `rules/project_overview_live.md` — curated, always-accurate snapshot; edit/delete outdated content to stay current.
    2) `rules/project_journal.md` — append-only log of what changed (including deletions); never remove entries.
- After every iteration, update both documents: keep the overview exact; append the journal entry.
- Internal development docs under `docs/` are not committed (see `.gitignore`). Use `rules/` for persistent standards.
- If a new standard emerges, add it to `rules/` before implementation so all agents/devs align.

## Git Commit History Rules (Backdating Policy)

- Project timeline: May 20, 2025 → June 18, 2025 (inclusive).
- All commits should be backdated within this window for a consistent history.
- Keep a linear history; small, logical commits mapped to the dated roadmap.

Example (PowerShell):
```
git add .
git commit --date "2025-05-20T10:00:00" -m "docs: initialize multi-agent architecture plan"
git commit --allow-empty --date "2025-05-21T16:30:00" -m "chore: planning updates and task breakdown"
```

Suggested cadence (adapt to actual work):
- 2025-05-20 to 2025-05-24: Docs & Schemas
- 2025-05-25 to 2025-05-29: Orchestrator & Memory
- 2025-05-30 to 2025-06-03: Tool Adapters (free APIs)
- 2025-06-04 to 2025-06-09: Core Agents (Activities, Routing, Hotel, Flight, Budget)
- 2025-06-10 to 2025-06-14: Scheduling, Weather, Validation, Outputs
- 2025-06-15 to 2025-06-18: Hardening, Docs, Demos

## Tech & Dependencies

- Python 3.10+ recommended.
- Pydantic (schemas), Requests/HTTPX (HTTP), dateutil (parsing), ics or similar (calendar export).
- LLM optional: for NL parsing if needed; minimize paid usage.
- Pin versions in requirements.txt when we implement; keep minimal footprint.

## Repository Structure (target)

```
src/
    orchestrator/     # central runner, schemas, blackboard
    agents/           # specialized agent modules (small, focused)
    tools/            # external API adapters (free/public)
    output/           # composers/exporters
    config/           # env/config loader utilities
test/               # all tests (unit, integration, contract)
docs/
```

## Coding Standards

- PEP 8; type hints everywhere; docstrings for all public functions/classes.
- No hard-coded keys/URLs—use env with safe defaults.
- Tool adapters: strict timeouts, retries with exponential backoff, caching.
- Respect API ToS: set User-Agent, throttle, avoid bulk scraping.

### Modularity Requirements

- Keep files small and cohesive; prefer composition over large classes.
- Separate concerns: agents do logic; tools do IO; orchestrator does control flow.
- Shared types and schemas live under `src/orchestrator` (or `src/config` for config).

### Testing Layout

- Place all tests under `test/` at the repo root.
- Mirror module structure (e.g., `test/test_agents_activities.py`, `test/tools/test_osrm_adapter.py`).
- Include fixtures for tool responses and schema samples.

## Tool Adapter Rules

- Each adapter defines: INPUT schema, OUTPUT schema, error classes, rate policy.
- Implement in-memory caching keyed by normalized request params.
- Log advisories without PII; never log raw tokens/keys.

### HTTP Client & Error-Handling Policy

- All outbound HTTP MUST use a shared client with:
    - Default timeout: 8s connect/read (configurable via TOOL_TIMEOUT_MS)
    - Retries: 2 with exponential backoff and jitter on 429/5xx/network errors (configurable via TOOL_RETRIES)
    - User-Agent: MiniTaskPlanner/{version} (+contact/URL), configurable via env; set Referer when applicable
    - Per-service etiquette: obey published QPS (e.g., Nominatim ~1 rps/IP)
- Structured exceptions for tools:
    - ToolTimeoutError
    - ToolRateLimitError (carry retry-after if provided)
    - ToolHTTPError(status, message)
    - ToolParseError
    - ToolUnavailableError
- Adapters must not crash orchestrator: return clear advisories and partial empty results on recoverable failures; record in Blackboard diagnostics.
- Never exceed free/public API policies; prefer caching and batch requests to reduce load.

## Agent Rules

- Validate inputs on entry; validate outputs on exit.
- No direct network calls—must go through tools.
- Stateless: read/write via Orchestrator/Blackboard only.
- Keep deterministic where possible; expose randomness seeds if used.

## Orchestrator & Memory

- Blackboard is the single source of truth; changes are atomic per step.
- Bounded re-planning cycles (default: 3) to avoid loops.
- Conflicts are recorded with human-readable explanations and suggestions.

## Testing

- Unit tests for each agent and tool with fixtures.
- Integration tests for multi-leg scenarios with mocks.
- Contract tests for schemas (pydantic) and tool I/O.
- Negative tests: rate limits, timeouts, missing data.

## Security & Privacy

- Environment variables for keys; `.env.example` documents variables.
- Optional IP-based origin detection; disabled by default.
- Strip PII from logs; allow users to purge local cache/state.

## Contribution Workflow

- Branching: feature branches allowed; small, focused PRs.
- Commits: conventional messages (feat, fix, docs, chore, test, refactor).
- Reviews: include tests and docs deltas for agent/tool changes.

## Performance & Rate Limits

- Cache geocoding, weather, routing queries.
- Respect per-service QPS; implement jitter and backoff.
- Batch where possible (e.g., weather for multiple days in one call).

## Definition of Done

- Docs updated and consistent with behavior.
- Types and schemas validated; tests passing.
- No secrets in code; env template updated.
- Handles at least: simple single-city, multi-leg with per-leg constraints, must-visits, and budget allocation.
