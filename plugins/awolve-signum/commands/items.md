---
description: List a project's items of every kind — implementation, bug, activity — with one number series and shared statuses
---

# /items

List a project's items in the new shape: every kind in one number series, with each item's kind and shared status. Bugs show their bug number beside their item number, e.g. `#74 (Bug #1)`.

This needs a Signum server with item types and shared statuses. On an older one the command says so; use `/awolve-signum:backlog` and `/awolve-signum:bugs` there.

## Instructions

Parse the user's argument. Expected forms:

- nothing — every configured project.
- `<project-id>` — one project.

Optional flags:

- `--kind implementation,bug,activity` — only these kinds (comma-separated or repeated).
- `--state S` — only items in that status. Shared statuses: `new`, `planned`, `in_progress`, `blocked`, `ready_for_testing`, `completed`, `archived`. Old values (`idea`, `open`, `ready_for_retest`…) work too. `ready_for_testing` finds both items waiting for testing and bugs waiting for retest.
- `--source widget` — only items filed through a feedback widget.
- `--all` — include done items (completed, archived). Without it, and without `--state`, only open ones are listed.
- `--json` — machine-readable output.

Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py items [<project-id>] [--kind K] [--state S] [--source widget] [--all] [--json]
```

Each line shows the number, kind, status label, title and assignee. Use `/awolve-signum:item` for the full record.

## The kinds

- **implementation** — a change to something deployed: code, config, infrastructure.
- **bug** — something that should work and does not.
- **activity** — work that changes no system: a training, a workshop, a signature. It has no testing step.
