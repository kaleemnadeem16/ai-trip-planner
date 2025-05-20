# Rules Folder

The `rules/` folder defines project-wide standards, working agreements, and operational practices. Before implementing any feature, read the rules and update them if a new standard is needed.

- Always consult rules before coding or refactoring.
- Propose new rules via PRs and document rationale.
- Keep rules concise, actionable, and current.

## Task Tracking & Switching

- Use `rules/task_tree.md` as the live task tree. Update it when:
	- starting a task ([~])
	- completing a task ([x])
	- pausing/switching a task ([↺]) with a one-line reason
- Every switch must be noted in `rules/project_journal.md` with date, reason, and what to resume next.
- Keep the backlog in `task_tree.md` tidy; move items between Today/Backlog as priorities change.

## Operational Artifacts (Keep Updated)

- `rules/task_tree.md` — Live task list with statuses and short notes. Source of truth for “what’s active now.”
- `rules/project_journal.md` — Append-only chronological log of decisions, switches, and notable changes.
- `rules/project_overview_live.md` — Curated snapshot of architecture, modules, and integrations; update when modules are added/removed/renamed.

Maintenance cadence:
- Update task_tree.md immediately upon starting/completing/switching tasks.
- Append to project_journal.md at the end of each iteration or significant switch.
- Refresh project_overview_live.md when a new module is added (e.g., src/utils/http_client.py) or responsibilities change.
