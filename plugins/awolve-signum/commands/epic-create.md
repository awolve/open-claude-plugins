---
description: Create an epic in a project (a level above features)
argument-hint: [project-id] [title]
---

# /awolve-signum:epic-create

Create an epic: a named body of work that groups features and items. It needs the same right as creating a backlog item.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask. Ask for a title if none was given.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epic-create <project-id> "<title>" [--description "<text>"] [--status idea|planned|in_progress|completed|archived] [--due YYYY-MM-DD] [--owner <email>]
```

- `--status` defaults to `idea`.
- `--due` sets a due date (internal users only; others get `timing_forbidden`).
- `--owner` names the person who owns the epic. They must have signed in to Signum once and be able to open the project.

The CLI prints the new epic's number (`E3`) and its portal link. Use that number with `/awolve-signum:epic-set` to put features or items under it, and with `backlog-add … --epic E3` to file a new item directly under it.

**A Signum service from before real epics** has no epic API: the CLI says so and creates nothing. Don't fall back to creating an item marked as an epic.
