---
description: Update a backlog item's title, description, priority, status, assignee, or epic flag
---

# /awolve-spec:backlog-update

Edit fields on an existing backlog item. Use this when the framing of an item has shifted, the priority has changed, the status needs to advance, or you want to promote/demote the epic flag without going through the portal.

## Instructions

Parse the user's argument. Expected forms:

- `<project> <item> <fields>` — explicit project + item ref + one or more fields
- `<item> <fields>` — use the configured project (only when one is configured)

Item references accept UUIDs or `#N` numeric form (with or without `#`).

At least one field flag is required: `--title`, `--description`, `--priority` (low|medium|high), `--status` (idea|planned|in_progress|completed|archived), `--epic` (true|false), `--assignee <email>`, `--unassign`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-update <project-id> <item-id-or-#N> [--title T] [--description T] [--priority P] [--status S] [--epic true|false] [--assignee EMAIL | --unassign]
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
```

## Notes

- To reparent an item under a different epic, use `/awolve-spec:backlog-set-parent` — clearer error reporting and validation.
- **Assignment is optional and validated.** The assignee must be a portal user who can see the project: internal Awolve users always qualify; external users need project access first. `assignee_not_found` means they've never signed in to the portal; `assignee_no_access` means grant them access, then assign.
- `--assignee` and `--unassign` are mutually exclusive. Omitting both leaves the current assignee untouched.
- Server-side constraints on `--epic`: epics must be top-level (no parent), can't toggle on an item that has children, can't demote-with-children.
- To remove an item entirely, use `/awolve-spec:backlog-delete` (soft-delete).
- The server records each change in the audit log.
