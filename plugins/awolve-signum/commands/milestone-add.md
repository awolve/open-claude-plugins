---
description: Plan an epic or a feature into a deadline (its items follow it), or put items in one
argument-hint: [project-id] [deadline]
---

# /awolve-signum:milestone-add

Plan work into a deadline. A piece of work is in at most one deadline, so work already in another one moves here. Only the deadline changes. Internal users only.

## Instructions

Determine the project as usual, and name the deadline by its name or id. Then give exactly one of:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --epic E3
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --feature <feature-name>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --items 12,15
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --epic-items E3
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-add <project-id> <deadline-name-or-id> --feature-items <feature-name>
```

- `--epic` and `--feature` plan the epic or feature **itself** into the deadline. This works before any items exist. Its items follow it unless they have a deadline of their own, and so do items added later. A feature with no deadline of its own follows its epic's.
- `--items` takes item numbers (or ids), comma-separated, and puts those items in the deadline themselves.
- `--epic-items` and `--feature-items` add each **open** item of that epic or feature one by one, as `--epic` and `--feature` did before. The epic or feature itself is not planned.
- A **date** holds no work: the service refuses with `milestone_is_date`.
- A service that can't plan an epic or a feature itself yet says so; use `--epic-items` / `--feature-items` there.

The CLI says what was planned and how many items follow it, or how many items were added, moved from another deadline, or already in it. A deadline's progress counts the lowest level it holds: items, else features, else epics. To move one item out again, use `backlog-update <project-id> '#N' --unmilestone`.
