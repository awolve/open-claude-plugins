---
description: Update a backlog item's title, description, priority, status, assignee, epic flag, or deployment info (stage + URL)
---

# /awolve-spec:backlog-update

Edit fields on an existing backlog item. Use this when the framing of an item has shifted, the priority has changed, the status needs to advance, or you want to promote/demote the epic flag without going through the portal.

## Instructions

Parse the user's argument. Expected forms:

- `<project> <item> <fields>` — explicit project + item ref + one or more fields
- `<item> <fields>` — use the configured project (only when one is configured)

Item references accept UUIDs or `#N` numeric form (with or without `#`).

At least one field flag is required: `--title`, `--description`, `--priority` (low|medium|high), `--status` (idea|planned|in_progress|ready_for_testing|completed|archived), `--epic` (true|false), `--assignee <email>`, `--unassign`, or one of the tag flags below.

**Tags:** `--tags a,b` replaces the whole set; `--add-tag T` and `--remove-tag T` are repeatable deltas applied against whatever the item wears right now; `--clear-tags` removes them all. `--tags` cannot be combined with `--add-tag`/`--remove-tag` — one replaces, the others adjust. Tags must already exist on the project: an unknown name fails with `tag_not_found` and a list of close matches, because coining a tag is a separate, permission-gated act (`/awolve-spec:tag-create`).

**Timing (spec 023, internal users only):** `--start YYYY-MM-DD`, `--due YYYY-MM-DD`, `--estimate HOURS` (0–9999.99, at most two decimals), and their valueless twins `--clear-start`, `--clear-due`, `--clear-estimate`. A start date after a due date is rejected — checked against the item's resulting state, so moving *either* date across the other fails. External users get `timing_forbidden`.

**Deployment info (spec 033):** `--deployed-stage preview|staging|production` and `--deployed-url <url>` record where the implementation currently runs — set together (a stage flip that kept the old URL would point at a torn-down preview host); the CLI stamps the deploy time automatically. `--clear-deployment` removes the fact. The stage is not a status: it says where the code runs, not who acts next.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update <project-id> <item-id-or-#N> [--title T] [--description T] [--priority P] [--status S] [--epic true|false] [--assignee EMAIL | --unassign] [--tags a,b | --add-tag T | --remove-tag T | --clear-tags] [--deployed-stage S --deployed-url U | --clear-deployment]
```

Examples:

```bash
# Reframe a stale item
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --title "Edit/delete affordance for backlog items"

# Bump priority and mark in-progress
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --priority high --status in_progress

# Replace the description
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --description "Add backlog-update and backlog-delete to the CLI."

# Promote an item to an epic
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --epic true

# Put it on someone's plate — or take it off
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --assignee michael.dovland@awolve.ai
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --unassign

# Label it, un-label it, or set the labels outright
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --add-tag billing --add-tag "Needs UX"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --remove-tag "Needs UX"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update spec-service 14 --tags billing,regression
```

## Notes

- To reparent an item under a different epic, use `/awolve-spec:backlog-set-parent` — clearer error reporting and validation.
- **Assignment is optional and validated.** The assignee must be a portal user who can see the project: internal Awolve users always qualify; external users need project access first. `assignee_not_found` means they've never signed in to the portal; `assignee_no_access` means grant them access, then assign.
- `--assignee` and `--unassign` are mutually exclusive. Omitting both leaves the current assignee untouched.
- Server-side constraints on `--epic`: epics must be top-level (no parent), can't toggle on an item that has children, can't demote-with-children.
- **Applying a tag needs only the right to edit the item** — it is the tag *vocabulary* that is permission-gated, not its use. See `/awolve-spec:tags` for the project's list.
- To remove an item entirely, use `/awolve-spec:backlog-delete` (soft-delete).
- The server records each change in the audit log.
