---
description: Put items in a deadline — single items, or an epic's or a feature's open items
argument-hint: [project-id] [deadline]
---

# /awolve-signum:milestone-add

Put items in a deadline. An item is in at most one deadline, so an item already in another one moves here. Only the deadline changes on each item. Internal users only.

## Instructions

Determine the project as usual, and name the deadline by its name or id. Then give exactly one of:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --items 12,15
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --epic E3
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --feature <feature-name>
```

- `--items` takes item numbers (or ids), comma-separated.
- `--epic` and `--feature` add each **open** item of that epic or feature in this project. The epic or feature itself is never put in the deadline, so the deadline's counts stay counts of items.
- A **date** holds no items: the service refuses with `milestone_is_date`.

The CLI says how many items were added, how many moved from another deadline, and how many were already in it. To move one item out again, use `backlog-update <project-id> '#N' --unmilestone`.
