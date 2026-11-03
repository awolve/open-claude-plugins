---
description: List a project's milestones (deadlines and dates) with progress and overdue
argument-hint: [project-id]
---

# /awolve-spec:milestones

List a project's milestones by date. A milestone is a **deadline**, which holds the items due by then, or a plain **date** worth knowing (a go-live, a steering group), which holds none.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestones <project-id> [--json]
```

Each row shows the date, the kind, the name, and for a deadline its progress (`1/5 items done`, or `0/3 features done` when it holds no items yet: newer services count the lowest level a deadline holds), `nothing planned yet`, or `overdue` when its date has passed with items open; for a date, `upcoming` or `passed`. `--json` prints the service's milestones with progress and state.

Most items are in no deadline. That is normal (they are "Unplanned"), not a problem to report.
